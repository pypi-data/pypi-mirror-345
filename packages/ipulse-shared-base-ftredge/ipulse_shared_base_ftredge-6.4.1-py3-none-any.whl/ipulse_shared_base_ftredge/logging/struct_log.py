import traceback
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any,Union, Tuple
from ipulse_shared_base_ftredge.enums  import (ReviewStatus, LogLevel, Unit,
                                        ProgressStatus, Alert, Action, Resource, DataResource)
from ipulse_shared_base_ftredge.utils import to_enum, any_as_str_or_none

### Created on: 25/12/2024 (from ContextLog)

class StructLog:
    def __init__(
        self,
        level: Union[LogLevel,str],
        action: Optional[Union[Action,str]] = None,
        resource: Optional[Union[Resource,str]] = None,
        source: Optional[Union[Resource,str]] = None,  # Modified type
        destination: Optional[Union[Resource,str]] = None,  # Modified type
        progress_status: Optional[ProgressStatus] = None,
        alert: Optional[Alert] = None,
        q: Optional[Union[int, float]] = 1,
        q_unit: Optional[Unit] = None,
        log_review_status: Optional[ReviewStatus] = ReviewStatus.OPEN,
        collector_id: Optional[Union[str, int]] = None,
        task_id: Optional[Union[str, int]] = None,
        base_context: Optional[str] = None,
        context: Optional[str] = None,
        description: Optional[Any] = None,
        note: Optional[Any] = None,
        systems_impacted:Optional[List[str]] = None,
        e: Optional[Exception] = None,
        e_type: Optional[str] = None,
        e_message: Optional[str] = None,
        e_traceback: Optional[str] = None,
        max_field_len: Optional[int] = 8000
    ):
        
        self._max_field_len = max_field_len if max_field_len is not None and isinstance(max_field_len, int ) and max_field_len > 0 else 8000
        self._truncated = False
        # Handle exception information
        if e is not None:
            e_type = type(e).__name__ if e_type is None else e_type
            e_message = str(e) if e_message is None else e_message
            e_traceback = traceback.format_exc() if e_traceback is None else self._to_sized_str(e_traceback)
            
            # Incorporate "caused by" into e_message
            caused_by = f"Caused by: {type(e).__name__}: {str(e)}"
            e_message = f"{e_message}\n{caused_by}" if e_message else caused_by

        elif not e_traceback and (e_type or e_message):
            e_traceback = traceback.format_exc()
        
         # Convert level - required field
        self._level = to_enum(level, LogLevel, required=True, default =LogLevel.NOTSET)

        # Convert optional enums - allow None
        self._action = to_enum(value=action, enum_class=Action, default=Alert.UNKNOWN)
        self._resource = to_enum(resource, Resource, default=DataResource.UNKNOWN)
        self._source = to_enum(source, Resource)  # Convert to enum if string
        self._destination = to_enum(destination, Resource)  # Convert to enum if string
        self._progress_status = to_enum(progress_status, ProgressStatus, default=ProgressStatus.UNKNOWN)
        self._alert = to_enum(alert, Alert, default=Alert.UNKNOWN)
        self._log_review_status = to_enum(log_review_status, ReviewStatus, default=ReviewStatus.OPEN)

        self._q = q
        self._q_unit = to_enum(q_unit, Unit)

        # Convert basic fields
        self._collector_id = self._to_sized_str(collector_id)
        self._task_id = self._to_sized_str(task_id)
        self._base_context = self._to_sized_str(base_context)
        self._context = self._to_sized_str(context)
        self._description = self._to_sized_str(description)
        self._note = self._to_sized_str(note)

         # Convert systems_impacted using _convert_systems_impacted
        self._systems_impacted = self._to_sized_str(self._convert_systems_impacted(systems_impacted))
        # Exception fields
        self._exception_type = self._to_sized_str(e_type)
        self._exception_message = self._to_sized_str(e_message)
        self._exception_traceback =  self._format_traceback(e_traceback=e_traceback)

        # Timestamp
        self._timestamp = datetime.now(timezone.utc).isoformat()
        


    @property
    def level(self) -> LogLevel:
        return self._level

    @level.setter
    def level(self, value: Union[LogLevel, str]):
        self._level = to_enum(value, LogLevel, required=True)


    @property
    def resource(self) -> Optional[Resource]:
        return self._resource

    # @resource.setter
    # def resource(self, value: Optional[Union[Resource, str]]):
    #     self._resource = to_enum(value, Resource)

    @property
    def source(self) -> Optional[Resource]:
        """Get source resource"""
        return self._source

    @source.setter
    def source(self, value: Optional[Union[Resource,str]]) -> None:
        """Set source resource. Accepts Resource enum or string."""
        self._source = to_enum(value, Resource)

    @property
    def destination(self) -> Optional[Resource]:
        """Get destination resource"""
        return self._destination

    @destination.setter
    def destination(self, value: Optional[Union[Resource,str]]) -> None:
        """Set destination resource. Accepts Resource enum or string."""
        self._destination = to_enum(value, Resource)

    @property
    def action(self) -> Optional[Action]:
        return self._action

    # @action.setter
    # def action(self, value: Optional[Union[Action, str]]):
    #     self._action = to_enum(value, Action)

    @property
    def progress_status(self) -> Optional[ProgressStatus]:
        return self._progress_status

    # @progress_status.setter
    # def progress_status(self, value: Optional[Union[ProgressStatus, str]]):
    #     self._progress_status = to_enum(value, ProgressStatus)

    @property
    def alert(self) -> Optional[Alert]:
        return self._alert

    # @alert.setter
    # def alert(self, value: Optional[Union[Alert, str]]):
    #     self._alert = to_enum(value, Alert)

    @property
    def log_review_status(self) -> ReviewStatus:
        return self._log_review_status

    @log_review_status.setter
    def log_review_status(self, value: ReviewStatus):
        self._log_review_status = to_enum(value, ReviewStatus, default=ReviewStatus.OPEN)

    @property
    def q(self) -> Optional[Union[int, float]]:
        return self._q
    
    @q.setter
    def q(self, value: Optional[Union[int, float]]):
        self._q = value

    @property
    def q_unit(self) -> Optional[Unit]:
        return self._q_unit
    
    @q_unit.setter
    def q_unit(self, value: Optional[Union[Unit, str]]):
        self._q_unit = to_enum(value, Unit)

    # Identification attributes
    @property
    def collector_id(self) -> Optional[Union[str, int]]:
        return self._collector_id

    @collector_id.setter
    def collector_id(self, value: Optional[Union[str, int]]):
        self._collector_id = self._to_sized_str(value)

    @property
    def task_id(self) -> Optional[Union[str, int]]:
        return self._task_id

    @task_id.setter
    def task_id(self, value: Optional[Union[str, int]]):
        self._task_id = self._to_sized_str(value)

    @property
    def base_context(self) -> Optional[str]:
        return self._base_context

    @base_context.setter
    def base_context(self, value: Optional[str]):
        self._base_context = self._to_sized_str(value)

    @property
    def context(self) -> Optional[str]:
        return self._context

    @context.setter
    def context(self, value: Optional[str]):
        self._context = self._to_sized_str(value)

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value):
        self._description = self._to_sized_str(value)

    @property
    def note(self) -> Optional[str]:
        return self._note

    @note.setter
    def note(self, value):
        self._note = self._to_sized_str(value)

    # Systems impacted
    @property
    def systems_impacted(self) -> Optional[str]:
        """
        Get the list of systems impacted. Which must be a list of strings.
        Those systems impacted are supposed to be the systems that are affected directly by the sequence logic leading to this log.
        Meaning a potential Rollback shall be for these systems only. Not for the whole pipeline."""
        return self._systems_impacted

    @systems_impacted.setter
    def systems_impacted(self, value: Optional[Union[str, List[str], None, Dict[str, str]]]):
        """
        Set the list of systems impacted. Which must be a list of strings.
        Those systems impacted are supposed to be the systems that are affected directly by the sequence logic leading to this log.
        Meaning a potential Rollback shall be for these systems only. Not for the whole pipeline."""

        self._systems_impacted = self._to_sized_str(self._convert_systems_impacted(value))


    # Exception related
    @property
    def exception_type(self) -> Optional[str]:
        return self._exception_type

    # @exception_type.setter
    # def exception_type(self, value: Optional[str]):
    #     self._exception_type = self._to_sized_str(value)

    @property
    def exception_message(self) -> Optional[str]:
        return self._exception_message

    # @exception_message.setter
    # def exception_message(self, value: Optional[str]):
    #     self._exception_message = self._to_sized_str(value)

    @property
    def exception_traceback(self) -> Optional[str]:
        return self._exception_traceback

    # @exception_traceback.setter
    # def exception_traceback(self, value: Optional[str]):
    #     self._exception_traceback = self._format_traceback(value)

    @property
    def max_field_len(self) -> int:
        return self._max_field_len
    
    @max_field_len.setter
    def max_field_len(self, value: int):
        if not isinstance(value, int) or value <= 0:
            return
        self._max_field_len = value

    # Timestamp
    @property
    def timestamp(self) -> str:
        return self._timestamp

    # @timestamp.setter
    # def timestamp(self, value: str):
    #     self._timestamp = self._to_sized_str(value)

    @property
    def truncated(self) -> bool:
        return self._truncated
    
    @truncated.setter
    def truncated(self, value: bool):
        self._truncated = value

    def getEvent(self, exclude_none: bool = True, as_dict: bool = False, with_q=False) -> Union[Dict[str, Any], Tuple[Any, ...]]:
        """
        Get Event enums as tuple (default) or dictionary.

        Args:
            exclude_none (bool): Whether to exclude None values.
            as_dict (bool): Whether to return the result as a dictionary.

        Returns:
            Union[Dict[str, Any], Tuple[Any, ...]]: Event data as a tuple (default) or dictionary.
        """
        event_details = {
            "level": self.level.name if self.level and not isinstance(self.level, str) else self.level,
            "action": self.action.name if self.action and not isinstance(self.action, str) else self.action,
            "resource": self.resource.name if self.resource and not isinstance(self.resource, str) else self.resource,
            "source": self.source.name if self.source and not isinstance(self.source, str) else self.source,  # Add source
            "destination": self.destination.name if self.destination and not isinstance(self.destination, str) else self.destination,  # Add destination
            "progress_status": self.progress_status.name if self.progress_status and not isinstance(self.progress_status, str) else self.progress_status,
            "alert": self.alert.name if self.alert and not isinstance(self.alert, str) else self.alert
        }

        if with_q:
            event_details["q"] = self.q
            event_details["q_unit"] = self.q_unit.name if self.q_unit and not isinstance(self.q_unit, str) else self.q_unit

        if exclude_none:
            # Filter out None values
            event_details = {key: value for key, value in event_details.items() if value is not None}

        if as_dict:
            return event_details
        return tuple(event_details.values())


    def _truncate_string(self, s: str, max_len: int) -> str:
        if not isinstance(s, str) or len(s) <= max_len:
            return s
        
        self.truncated=True
        trunc_msg="... (truncated) ..."
        if max_len<250:
            trunc_msg="..."
        max_len = max_len - len(trunc_msg)
        half = max_len // 2

        return f"{s[:half]}{trunc_msg}{s[-half:]}"
    
    def _to_sized_str(self, value: Any) -> Optional[str]:
        """Convert value to string safely and truncate if it exceeds max_field_len."""
        s = any_as_str_or_none(value)
        if s and len(s) > self.max_field_len:
            s = self._truncate_string(s, self.max_field_len)
        return s
    
    
    def _convert_systems_impacted(self, value: Any) -> str:
        """Convert systems_impacted to a single string safely."""
        if value is None:
            return None
        if isinstance(value, str):
            return f"system(s): {value}"
        if isinstance(value, list):
            return f"{len(value)} system(s): {' _;_ '.join(map(str, value))}"
        if isinstance(value, dict):
            return f"{len(value)} system(s): {' _;_ '.join(f'{k}: {v}' for k, v in value.items())}"
        return str(value)


    def _format_traceback(self, e_traceback, e_message:Optional[str]=None ) -> Optional[str]:
        """Format traceback efficiently  for logging"""

        if not e_traceback or e_traceback == 'None\n':
            return None

            # Check if the traceback is within the limits
        # if len(e_traceback) <=self.max_field_len:
        #     return e_traceback
        
        # EXTRA OPTIMIZATION WHICH IS NOT NEEDED FOR MSOT CASES
        # traceback_lines = e_traceback.splitlines()

        # # Remove lines that are part of the exception message if they are present in traceback
        # message_lines = e_message.splitlines() if e_message else []
        # if message_lines:
        #     for message_line in message_lines:
        #         if message_line in traceback_lines:
        #             traceback_lines.remove(message_line)

        # # Filter out lines from third-party libraries (like site-packages)
        # filtered_lines = [line for line in traceback_lines if "site-packages" not in line]

        # # Combine standalone bracket lines with previous or next lines
        # combined_lines = []
        # for line in filtered_lines:
        #     if line.strip() in {"(", ")", "{", "}", "[", "]"} and combined_lines:
        #         combined_lines[-1] += " " + line.strip()
        #     else:
        #         combined_lines.append(line)


        # Ensure the total length doesn't exceed MAX_TRACEBACK_LENGTH
        if len(e_traceback) > self.max_field_len:
            self.truncated = True
            trunc_msg="\n... (truncated) ...\n"
            truncated_length = self.max_field_len - len(trunc_msg)
            half_truncated_length = truncated_length // 2
            e_traceback = (
                e_traceback[:half_truncated_length] +
                trunc_msg +
                e_traceback[-half_truncated_length:]
            )
        return e_traceback
    
    def _create_initial_dict(self) -> Dict[str, Any]:
        """Create initial dictionary with all values from properties"""
        if not self.level:
            self.level = LogLevel.NOTSET
        return {
            "level": self.level.name,
            "level_code": self.level.value, # Enum
            "base_context": self.base_context,  # Already string from property
            "context": self.context ,  # Already string from property
            "action": self.action.name if self.action else None, # Enum
            "resource": self.resource.name if self.resource else None, # Enum
            "source": self.source.name if self.source else None,  # Add source
            "destination": self.destination.name if self.destination else None,  # Add destination
            "progress_status": self.progress_status.name if self.progress_status else None, # Enum
            "progress_status_code": self.progress_status.value if self.progress_status else None, # Enum
            "alert": self.alert.name if self.alert else None, # Enum
            "q": self.q if self.q else None,  # Already string from property
            "q_unit": self.q_unit.name if self.q_unit else None, # Enum
            "collector_id": self.collector_id if self.collector_id else None,  # Already string from property
            "task_id": self.task_id,  # Already string from property
            "description": self.description,  # Already string from property
            "note": self.note,  # Already string from property
            "systems_impacted": self.systems_impacted, # Already string from property
            "log_review_status": self.log_review_status.name if self.log_review_status else None,  # Enum
            "exception_type": self.exception_type,  # Already string from property
            "exception_message": self.exception_message,  # Already string from property
            "exception_traceback": self.exception_traceback,  # Already string from property
            "timestamp": self.timestamp,  # Already string from property
            "truncated": self.truncated
        }
    
    
    def to_dict(self,  byte_size_limit: Optional[float]= 256 * 1024 * 0.80, max_field_len: Optional[int]=None) -> Dict[str, Any]:
        """
        Convert StructLog to dictionary, respecting size limits.
        
        Args:
            size_limit: Total size limit in bytes (default 80% of CloudWatch/CloudLogging 256KB limit)
            max_field_len: Maximum length for any string field
        
        Returns:
            Dict containing log data, truncated if necessary to meet size constraints
        """

        if max_field_len is None or not isinstance(max_field_len, int) or max_field_len <= 0:
            max_field_len=self.max_field_len
        if byte_size_limit is None or not isinstance(byte_size_limit, (int, float)) or byte_size_limit <= 0:
            byte_size_limit = 256 * 1024 * 0.80 # 80% of 256KB

        log_dict = self._create_initial_dict()
        extra_allow_for_large_fields = 0
        extra_allow_ratio = 3 # Extra ratio for large fields because there is at least 3+1=4 times more shorter fields than large fields
        avg_field_size_allowed = byte_size_limit // len(log_dict)

        if avg_field_size_allowed > 150:
            extra_allow_for_large_fields = (avg_field_size_allowed - 150) * extra_allow_ratio

        max_field_len = min(max_field_len, avg_field_size_allowed + extra_allow_for_large_fields)
        
         # Try fast path - check if dict fits size limit

        if max_field_len>=self.max_field_len: # If max_field_len is not smaller than the default max_field_len
            try:
                serialized = json.dumps(log_dict, ensure_ascii=False).encode('utf-8')
                if len(serialized) <= byte_size_limit:
                    return log_dict
            except (TypeError, ValueError):
                pass
        
        # Slow path - process field by field
        return self._create_size_limited_dict(log_dict=log_dict, max_field_len=max_field_len, byte_size_limit=byte_size_limit)
    

    def _create_size_limited_dict(self, log_dict: Dict[str, Any], max_field_len: int, byte_size_limit: float) -> Dict[str, Any]:
        """Create dictionary with size limits enforced"""

        log_dict["truncated"] = True
        result = {}
        remaining_bytes = byte_size_limit
        fields = list(log_dict.items())

        # Priority fields - always include these
        priority_fields = {'level_name', 'level_code', 'truncated', 'collector_id', 'timestamp', 'context'}

        # Process priority fields first
        for key, value in fields[:]:
            if key in priority_fields:
                processed_value = self._process_field_value(value, max_field_len)
                approx_field_size = len(json.dumps({key: processed_value}).encode('utf-8'))
                if approx_field_size <= remaining_bytes:
                    result[key] = processed_value
                    remaining_bytes -= approx_field_size
                    fields.remove((key, value))
                # else:
                #    break  # Stop processing if we run out of space. Commented out to include as much as possible, perhaps smaller fields will fit

        if not fields:
            return result
        for key, value in fields:
            processed_value = self._process_field_value(value=value, max_len=max_field_len)
            approx_field_size = len(json.dumps({key: processed_value}).encode('utf-8'))
            if approx_field_size <= remaining_bytes:
                result[key] = processed_value
                remaining_bytes -= approx_field_size
            # else:
            #     break  # Stop processing if we run out of space. Commented out to include as much as possible, perhaps smaller fields will fit

    ############# TODO #############
    ######## ----->>>>>>> USE THIS ALTERNATIVE METHOD BELOW, IN CASE TRYING TO FIT AMOUNT OF INFORMATION TO CAPTURE IN SMALLER ALLOWED BYTE SIZE LOGS
    #     remaining_fields = len(fields)

    #     for key, value in fields:
    #         if remaining_fields > 0:
    #             max_size_per_field = remaining_size // remaining_fields
    #         else:
    #             max_size_per_field = 0

    #         field_sz = fast_field_size_estimate(key, value)
    #         if field_sz > max_size_per_field:
    #             value = truncate_string(value, max_size_per_field)
    #             field_sz = fast_field_size_estimate(key, value)

    #         result[key] = value
    #         remaining_size -= field_sz
    #         remaining_fields -= 1


        return result
    
    def _process_field_value(self, value: Any, max_len: int) -> Any:
        """Process field value ensuring string type for size checking"""
        if value is None:
            return None
        
        str_value = str(value)
        if len(str_value) > max_len:
            return self._truncate_string(str_value, max_len)
        return value

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def __repr__(self):
        return self.__str__()
