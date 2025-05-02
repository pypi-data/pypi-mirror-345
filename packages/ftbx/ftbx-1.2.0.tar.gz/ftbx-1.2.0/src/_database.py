"""

    PROJECT: flex_toolbox
    FILENAME: _database.py
    AUTHOR: David NAISSE
    DATE: November 12th, 2024

    DESCRIPTION: database class
"""

import logging
import os
from re import error
import sys
from typing import Any, Dict, List, Optional, Tuple, Generator
from contextlib import contextmanager
from tqdm import tqdm

import mysql.connector
from rich.logging import RichHandler

from src._consul import Consul
from src.utils import FTBX_LOG_LEVELS

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


class DatabaseSession:
    """Database session wrapper"""

    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

    def execute(self, query: str, params: Tuple = None) -> Any:
        """Execute a database query"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def commit(self) -> None:
        """Commit current transaction"""
        self.connection.commit()

    def rollback(self) -> None:
        """Rollback current transaction"""
        self.connection.rollback()

    def get_jobs(self, job_ids: List[int]) -> List[Dict]:
        """Get jobs from the database"""

        if not job_ids:
            logger.error("Empty job ids provided.")
            sys.exit(1)

        # process jobs in batches of 500 to avoid query length limitations
        BATCH_SIZE = 500 
        all_jobs = []
        
        for i in range(0, len(job_ids), BATCH_SIZE):
            batch_ids = job_ids[i:i + BATCH_SIZE]
            
            # create placeholders for the IN clause
            placeholders = ', '.join(['%s'] * len(batch_ids))
            
            # get jobs for this batch
            batch_jobs = self.execute(
                query=f"""
                SELECT 
                    ID_, 
                    JOB_STATE_, 
                    CLASS_, 
                    NAME_, 
                    ACTION_CONFIG_, 
                    WORKSPACE_, 
                    ACCOUNT_ 
                FROM MIO_JOB 
                WHERE ID_ IN ({placeholders})
                """,
                params=tuple(batch_ids)
            )
            
            all_jobs.extend(batch_jobs)
        
        # make sure we got all requested jobs
        if not len(job_ids) == len(all_jobs):
            logger.error(f"Requested {len(job_ids)} jobs but only {len(all_jobs)} were retrieved.")
            sys.exit(1)
        
        logger.info(f"Successfully retrieved {len(all_jobs)} jobs from database.")

        return all_jobs

    def fail_jobs(self, job_ids: List[int]) -> List[Dict]:
        """Fail jobs in the database"""

        # get current job states
        jobs = self.get_jobs(job_ids)
        failed_jobs = []
        
        for job in tqdm(jobs, desc="Failing jobs"):
            job_id = job['ID_']
            current_state = job['JOB_STATE_']
            job_class = job['CLASS_']
            
            # check if job can be failed
            if current_state == 'FAILED':
                logger.warning(f"Job `{job_id}` is already in FAILED state, skipping...")
                continue
            
            if current_state == 'COMPLETED':
                logger.warning(f"Job `{job_id}` is COMPLETED, skipping...")
                continue
            
            if job_class in ['MioSystemActionJob', 'MioTimedActionJob']:
                logger.warning(f"Job `{job_id}` is of type `{job_class}`, skipping...")
                continue
            
            # update job state to FAILED
            try:
                logger.debug(f"Updating job `{job_id}` state to `FAILED`")
                self.execute(
                    query="UPDATE MIO_JOB SET JOB_STATE_ = %s WHERE ID_ = %s",
                    params=('FAILED', job_id)
                )
                self.commit()
                
                # verify the update
                updated_job = self.execute(
                    query="SELECT ID_, JOB_STATE_ FROM MIO_JOB WHERE ID_ = %s",
                    params=(job_id,)
                )[0]
                
                if updated_job['JOB_STATE_'] != 'FAILED':
                    raise Exception(f"Failed to update job `{job_id}` - current state: `{updated_job['JOB_STATE_']}`")
                
                failed_jobs.append(job)
                logger.debug(f"Job `{job_id}` is now `FAILED`")
                
            except Exception as e:
                self.rollback()
                logger.error(f"Error failing job `{job_id}`: {str(e)}")
                raise

        return failed_jobs


class Database:
    """Database connection wrapper"""

    def __init__(self, consul: Consul) -> None:
        """Initialize Database connection"""
        self.consul = consul
        logger.debug("Initialized Database connection")

    def _create_connection(self) -> Tuple[Any, Any]:
        """Create a new database connection and cursor"""
        try:
            credentials = self.consul.get_db_credentials()
            connection = mysql.connector.connect(
                host=credentials["host"],
                port=credentials["port"],
                user=credentials["user"],
                password=credentials["password"],
                database=credentials["database"],
                connect_timeout=10,
            )
            cursor = connection.cursor(dictionary=True)
            logger.debug("Database connection established")
            return connection, cursor
        except Exception as e:
            if all(key in str(e) for key in ["Access denied for user", "using password: YES"]):
                logger.error(f"Not allowed to establish database connection. Please connect to the servers to run this command.")
                sys.exit(1)
            else:
                logger.error(f"Failed to establish database connection: {str(e)}")
            raise

    @contextmanager
    def session(self) -> Generator[DatabaseSession, None, None]:
        """Create a database session context manager"""
        connection, cursor = self._create_connection()
        try:
            yield DatabaseSession(connection, cursor)
        finally:
            cursor.close()
            connection.close()
            logger.debug("Database connection closed")

