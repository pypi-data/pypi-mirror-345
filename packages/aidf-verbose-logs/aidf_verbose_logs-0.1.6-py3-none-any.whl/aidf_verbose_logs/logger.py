from datetime import datetime
import inspect
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

import psycopg2


class AIDFVerboseLogger:
    def __init__(
        self,
        payload: Dict[str, Any],
        db_conn_str: str,
        db_schema: str,
        manifest_path: Optional[str] = "../scripts/manifest.xml",
    ):
        self.manifest_path = manifest_path
        self.payload = payload
        self.ai_service_name, self.module_name, self.component = self._read_manifest(
            manifest_path
        )

        (
            self.executionid,
            self.workspaceid,
            self.projectid,
            self.environmentid,
            self.userid,
        ) = self._get_values_from_payload(payload)

        self._total_records = 0
        self._processed_records = 0
        self._db_conn_str = db_conn_str
        self._db_schema = db_schema
        self.conn, self.cursor = self._connect_to_db(db_conn_str)
        self._ai_service_log_record = self._init_logs_data()

    def get__total_records_count(self) -> int:
        """
        Retrieves the total number of records.

        This method returns the value of the `_total_records` attribute, which holds the total number of records
        that are being processed.

        Returns:
            int: The total number of records.

        Raises:
            Exception: If an error occurs while retrieving the total records count, an exception will be raised.
        """
        try:
            return self._total_records
        except Exception as e:
            print(f"Error while getting total records count:\n{e}")
            raise e

    def get_processed_records_count(self) -> int:
        """
        Retrieves the number of processed records.

        This method returns the value of the `processed_records` attribute, which holds the number of records
        that have been processed so far.

        Returns:
            int: The number of processed records.

        Raises:
            Exception: If an error occurs while retrieving the processed records count, an exception will be raised.
        """
        try:
            return self._processed_records
        except Exception as e:
            print(f"Error while getting processed records count:\n{e}")
            raise e

    def set_total_records_count(self, total_records: int):
        """
        Sets the total number of records.

        This method sets the value of the `_total_records` attribute. It ensures that the input is an integer,
        and raises an exception if the input is not of type `int`.

        Args:
            _total_records (int): The total number of records to be set.

        Raises:
            ValueError: If the input `_total_records` is not an integer.
            Exception: If any other error occurs while setting the total records count.
        """
        try:
            if isinstance(total_records, int):
                self._total_records = total_records
            else:
                raise ValueError("Total records must be an integer.")
        except Exception as e:
            print(f"Error while setting total records count:\n{e}")
            raise e

    def increment_processed_records(self, processed_records: Optional[int] = 1):
        """
        Increments the count of processed records.

        This method increments the value of the `processed_records` attribute by the specified number (default is 1).
        It ensures that the input is an integer, and raises an exception if the input is not of type `int`.

        Args:
            processed_records (Optional[int]): The number of records to increment. Defaults to 1.

        Raises:
            ValueError: If the input `processed_records` is not an integer.
            Exception: If any other error occurs while incrementing the processed records count.
        """
        try:
            if isinstance(processed_records, int):
                self._processed_records += processed_records
            else:
                raise ValueError("Processed records must be an integer.")
        except Exception as e:
            print(f"Error while incrementing processed records count:\n{e}")
            raise e

    def log(self, log_description: str):
        """
        Logs the execution details of the AI service.

        This method constructs a log entry for the AI service execution, including details such as workspace ID, project ID,
        execution ID, and other relevant information. It inserts the log entry into the `AI_SERVICE_EXECUTION_LOGS` table in
        the database. The log description is provided as an argument.

        Args:
            log_description (str): A description of the log entry to be created.

        Returns:
            None

        Raises:
            Exception: If an error occurs while inserting the log entry into the database, an exception will be raised.
        """
        try:
            log_description.replace("%total_records%", str(self._total_records))
            log_description.replace("%processed_records%", str(self._processed_records))
            ai_ser_exec_logs = self._ai_service_log_record
            ai_ser_exec_logs["log_description"] = log_description
            now = datetime.now()
            for key in ["log_date", "created_date", "updated_date"]:
                ai_ser_exec_logs[key] = now

            insert_query = f"""
                INSERT INTO {self._db_schema}.AI_SERVICE_EXECUTION_LOGS (
                    LOG_TYPE, WORKSPACE_ID, PROJECT_ID, ENVIRONMENT_ID, EXECUTION_ID, AI_SERVICE_ID,
                    MODULE_COMPONENT_ID, LOG_DESCRIPTION, LOG_DATE, CREATED_BY, CREATED_DATE,
                    UPDATED_BY, UPDATED_DATE, ACTIVE_FLAG, TOTAL_RECORDS, PROCESSED_RECORDS, PROCESSED_DISPLAY_FLAG
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            insert_values = (
                ai_ser_exec_logs["log_type"],
                ai_ser_exec_logs["workspace_id"],
                ai_ser_exec_logs["project_id"],
                ai_ser_exec_logs["environment_id"],
                ai_ser_exec_logs["execution_id"],
                ai_ser_exec_logs["ai_service_id"],
                ai_ser_exec_logs["module_component_id"],
                ai_ser_exec_logs["log_description"],
                ai_ser_exec_logs["log_date"],
                ai_ser_exec_logs["created_by"],
                ai_ser_exec_logs["created_date"],
                ai_ser_exec_logs["updated_by"],
                ai_ser_exec_logs["updated_date"],
                ai_ser_exec_logs["active_flag"],
                self._total_records,
                self._processed_records,
                "N",
            )

            try:
                self.cursor.execute(insert_query, insert_values)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                print(f"ai_ser_exec_logs Insert failed:\n{e}")

        except Exception as e:
            print(f"There was an error in ai_service_logs:\n{e}")
            raise e

    def _read_manifest(
        self, manifest_path: Optional[str] = "../scripts/manifest.xml"
    ) -> Tuple[str, str, str]:
        """
        Reads and extracts values from the manifest.xml file.

        Returns:
            Tuple[str, str, str]: A tuple containing extracted values from the manifest:
              (ai_service_name, module_name, component).

        Raises:
            FileNotFoundError: If the manifest file does not exist at the specified path.
            IOError: If there's an error reading the manifest file.
            ValueError: If the required elements are not found in the manifest file.
        """
        try:
            # Walk up the call stack to find the first non-package file
            caller_file = None
            for frame_info in inspect.stack():
                file_path = frame_info.filename
                # Skip internal or venv files
                if "site-packages" not in file_path and ".venv" not in file_path:
                    caller_file = file_path
                    break

            if caller_file is None:
                raise RuntimeError("Unable to resolve the caller's script path.")

            caller_dir = Path(os.path.dirname(os.path.abspath(caller_file)))

            # Default manifest path if not already set
            manifest_path = getattr(self, "manifest_path", "scripts/manifest.xml")

            # Resolve the full path to the manifest file
            manifest_file_path = caller_dir / manifest_path

            if not manifest_file_path.is_file():
                raise FileNotFoundError(
                    f"Manifest file not found at: {manifest_file_path}"
                )

            # Read the content of the manifest file
            manifest_content = manifest_file_path.read_text()

            # Define patterns to extract specific values
            name_pattern = r"<Name>(.*?)</Name>"
            module_name_pattern = r"<Module_Name>(.*?)</Module_Name>"
            component_pattern = r"<Component>(.*?)</Component>"

            # Use regex to find the matches
            ai_service_name = re.search(name_pattern, manifest_content)
            module_name = re.search(module_name_pattern, manifest_content)
            component = re.search(component_pattern, manifest_content)

            # Check if matches were found
            if not ai_service_name or not module_name or not component:
                raise ValueError(
                    "Required elements <Name>, <Module_Name>, or <Component> not found in the manifest file."
                )

            return ai_service_name.group(1), module_name.group(1), component.group(1)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise
        except ValueError as e:
            print(f"Error: {e}")
            raise
        except IOError as e:
            print(f"Error reading file {manifest_path}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise

    def _get_values_from_payload(
        self, payload: Dict[str, Any]
    ) -> Tuple[str, str, str, str, str]:
        """
        Extracts specific values from the payload dictionary.

        Returns:
            Tuple[str, str, str, str, str]: A tuple containing extracted values from the payload:
                (executionid, workspaceid, projectid, environmentid, userid).
        """
        return (
            payload.get("executionid"),
            payload.get("workspaceid"),
            payload.get("projectid"),
            payload.get("environmentid"),
            payload.get("userid"),
        )

    def _connect_to_db(self, db_conn_str: str):
        """
        Establishes a connection to the database and returns the connection and cursor.

        Returns:
            tuple: A tuple containing the connection object and a cursor object.

        Raises:
            Exception: If there is an error while connecting to the database.
        """
        try:
            conn = psycopg2.connect(db_conn_str)
            return conn, conn.cursor()
        except psycopg2.Error as e:
            print(f"Error: {e}")
            raise Exception(f"Error connecting to database: {e}")

    def _init_logs_data(self):
        """
        This method handles the process of preparing and returning a payload for logging AI service execution details.
        It connects to the database, fetches required data (such as module component ID, AI service ID, and log type),
        and constructs a dictionary with the necessary log information.

        Steps:
        1. Establishes a connection to the database using the provided connection string.
        2. Fetches the `MODULE_COMPONENT_ID` for the given module and component from the `MODULE_COMPONENTS` table.
        3. Retrieves the `AI_SERVICE_ID` from the `AI_SERVICES` table based on the provided AI service name and module component ID.
        4. Retrieves the `LOG_TYPE` associated with the provided `executionid` from the `EXECUTION_LOGS` table.
        5. Constructs a dictionary containing the workspace ID, project ID, environment ID, execution ID, and other relevant information, which is returned for further processing.

        Returns:
        - A dictionary containing the prepared payload for logging, which includes:
          - `workspace_id`, `project_id`, `environment_id`, `execution_id`, etc.
          - `log_type` and other log-related information.

        Raises:
        - `Exception`: If any of the database queries fail or if necessary data (e.g., module/component IDs or AI service IDs) cannot be found, an exception is raised with an appropriate message.
        """

        try:
            module_com_id_query = f"""
                SELECT MODULE_COMPONENT_ID 
                FROM {self._db_schema}.MODULE_COMPONENTS 
                WHERE MODULE_NAME = '{self.module_name}' 
                  AND COMPONENT_NAME = '{self.component}'
            """
            self.cursor.execute(module_com_id_query)
            module_com_id_res = self.cursor.fetchone()
            if not module_com_id_res:
                print(
                    "No module component ID found for the given module and component."
                )
                raise Exception(
                    "Module component ID not found.", self.module_name, self.component
                )
            module_com_id = module_com_id_res[0]
            # breakpoint()

            # Fetch AI_SERVICE_ID
            ai_service_id_query = f"""
                SELECT DISTINCT(AI_SERVICE_ID) 
                FROM {self._db_schema}.AI_SERVICES 
                WHERE AI_SERVICE_NAME = '{self.ai_service_name}' 
                  AND MODULE_COMPONENT_ID = {module_com_id} 
                  AND ACTIVE_FLAG = 'Y'
            """
            self.cursor.execute(ai_service_id_query)
            ai_service_id_res = self.cursor.fetchone()
            if not ai_service_id_res:
                print(
                    "No AI service ID found for the given AI service name and module component ID."
                )
                raise Exception(
                    "AI service ID not found for the given AI service name.",
                    self.ai_service_name,
                )
            ai_service_id = ai_service_id_res[0]

            # Fetch LOG_TYPE
            log_type_query = f"""
                SELECT LOG_TYPE 
                FROM {self._db_schema}.EXECUTION_LOGS 
                WHERE LOG_TYPE_ID = {self.executionid}
            """
            self.cursor.execute(log_type_query)
            resp = self.cursor.fetchone()
            if not resp:
                print("No log type found for the given execution ID.", self.executionid)
                raise Exception("Log type not found.")
            log_type = resp[0] if resp else "template"

            curr_time = datetime.now()
            return {
                "workspace_id": int(self.workspaceid),
                "project_id": int(self.projectid),
                "environment_id": int(self.environmentid),
                "execution_id": int(self.executionid),
                "module_component_id": module_com_id,
                "ai_service_id": ai_service_id,
                "log_type": log_type,
                "log_description": "",
                "log_date": curr_time,
                "created_by": int(self.userid),
                "updated_by": int(self.userid),
                "created_date": curr_time,
                "updated_date": curr_time,
                "active_flag": "Y",
            }

        except Exception as e:
            print(f"Error while preparing AI service execution log payload:\n{e}")
            raise e

    def __del__(self):
        try:

            if self._processed_records == self._total_records:
                self.log(f"Processed all {self._total_records} file(s)")
            else:
                self.log(
                    f"Processed only {self._processed_records}/{self._total_records}. There was an error while processing remaining {self._total_records - self._processed_records} file(s)"
                )

            self.log(f"{self.ai_service_name} execution completed successfully.")

            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error while closing the database connection:\n{e}")
            raise e
