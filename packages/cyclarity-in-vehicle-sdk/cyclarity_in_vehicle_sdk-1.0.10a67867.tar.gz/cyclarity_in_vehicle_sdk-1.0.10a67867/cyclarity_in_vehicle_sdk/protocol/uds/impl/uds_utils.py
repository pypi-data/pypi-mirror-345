import time
from typing import Optional, Type, Union
from pydantic import Field
from udsoncan.BaseService import BaseService
from udsoncan.Request import Request
from udsoncan.services import (ECUReset, 
                               ReadDataByIdentifier, 
                               RoutineControl, 
                               SecurityAccess, 
                               TesterPresent, 
                               WriteDataByIdentifier, 
                               DiagnosticSessionControl)
from udsoncan.common.DidCodec import DidCodec
from udsoncan import latest_standard
from udsoncan.exceptions import ConfigError
from cyclarity_in_vehicle_sdk.protocol.uds.base.uds_utils_base import (UdsSid, 
                                                                       NegativeResponse, 
                                                                       NoResponse, 
                                                                       RoutingControlResponseData, 
                                                                       SessionControlResultData, 
                                                                       UdsUtilsBase, 
                                                                       InvalidResponse, 
                                                                       RawUdsResponse, 
                                                                       UdsResponseCode,
                                                                       RdidDataTuple)
from cyclarity_in_vehicle_sdk.communication.isotp.impl.isotp_communicator import IsoTpCommunicator
from cyclarity_in_vehicle_sdk.communication.doip.doip_communicator import DoipCommunicator
from cyclarity_in_vehicle_sdk.protocol.uds.models.uds_models import SECURITY_ALGORITHM_BASE, SESSION_ACCESS, UdsStandardVersion

DEFAULT_UDS_OPERATION_TIMEOUT = 2
RAW_SERVICES_WITH_SUB_FUNC = {value: type(name, (BaseService,), {'_sid':value, '_use_subfunction':True}) for name, value in UdsSid.__members__.items()}  
RAW_SERVICES_WITHOUT_SUB_FUNC = {value: type(name, (BaseService,), {'_sid':value, '_use_subfunction':False}) for name, value in UdsSid.__members__.items()}  

class MyAsciiCodec(DidCodec):
    def __init__(self):
        pass

    def encode(self, string_ascii: str) -> bytes:
        if not isinstance(string_ascii, str):
            raise ValueError("AsciiCodec requires a string for encoding")

        return bytes.fromhex(string_ascii)

    def decode(self, string_bin: bytes) -> str:
        return string_bin.hex()

    def __len__(self) -> int:
        raise DidCodec.ReadAllRemainingData

class UdsUtils(UdsUtilsBase):
    data_link_layer: Union[IsoTpCommunicator, DoipCommunicator]
    attempts: int = Field(default=1, ge=1, description="Number of attempts to perform the UDS operation if no response was received")

    def setup(self) -> bool:
        """setup the library
        """
        return self.data_link_layer.open()
    
    def teardown(self):
        """Teardown the library
        """
        self.data_link_layer.close()
    
    def session(self, session: int, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT, standard_version: UdsStandardVersion = UdsStandardVersion.ISO_14229_2020) -> SessionControlResultData:
        """	Diagnostic Session Control

        Args:
            timeout (float): timeout for the UDS operation in seconds
            session (int): session to switch into
            standard_version (UdsStandardVersion, optional): the version of the UDS standard we are interacting with. Defaults to ISO_14229_2020.
            
        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            SessionControlResultData
        """
        request = DiagnosticSessionControl.make_request(session=session)
        response = self._send_and_read_response(request=request, timeout=timeout)   
        interpreted_response = DiagnosticSessionControl.interpret_response(response=response, standard_version=standard_version)
        return interpreted_response.service_data
    
    def transit_to_session(self, route_to_session: list[SESSION_ACCESS], timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT, standard_version: UdsStandardVersion = UdsStandardVersion.ISO_14229_2020) -> bool:
        """Transit to the UDS session according to route

        Args:
            route_to_session (list[SESSION_ACCESS]): list of UDS SESSION_ACCESS objects to follow
            timeout (float): timeout for the UDS operation in seconds
            standard_version (UdsStandardVersion, optional): the version of the UDS standard we are interacting with. Defaults to ISO_14229_2020.

        Returns:
            bool: True if succeeded to transit to the session, False otherwise 
        """
        for session in route_to_session:
            try:    
                change_session_ret = self.session(session=session.id, timeout=timeout, standard_version=standard_version)
                if change_session_ret.session_echo != session.id:
                    self.logger.warning(f"Unexpected session ID echo, expected: {hex(session.id)}, got {hex(change_session_ret.session_echo)}")
                
                # try to elevate security access if algorithm is provided for this session
                if session.elevation_info and session.elevation_info.security_algorithm:
                    try:
                        self.security_access(security_algorithm=session.elevation_info.security_algorithm, timeout=timeout)
                    except Exception as ex:
                        self.logger.warning(f"Failed to get security access, continuing without. error: {ex}")

            except Exception as ex:
                self.logger.warning(f"Failed to switch to session: {hex(session.id)}, what: {ex}")
                return False

        return True
    
    def ecu_reset(self, reset_type: int, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> bool:
        """The service "ECU reset" is used to restart the control unit (ECU)

        Args:
            timeout (float): timeout for the UDS operation in seconds
            reset_type (int): type of the reset (1: hard reset, 2: key Off-On Reset, 3: Soft Reset, .. more manufacture specific types may be supported)

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            bool: True if ECU request was accepted, False otherwise.
        """
        request = ECUReset.make_request(reset_type=reset_type)
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = ECUReset.interpret_response(response=response)
        return interpreted_response.service_data.reset_type_echo == reset_type

    def read_did(self, didlist: Union[int, list[int]], timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> list[RdidDataTuple]:
        """	Read Data By Identifier

        Args:
            timeout (float): timeout for the UDS operation in seconds
            didlist (Union[int, list[int]]): List of data identifier to read.

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            dict[int, str]: Dictionary mapping the DID (int) with the value returned
        """
        request = ReadDataByIdentifier.make_request(didlist=didlist, didconfig=None)
        response = self._send_and_read_response(request=request, timeout=timeout)
        return self._split_dids(didlist=didlist, data_bytes=response.data)

    def routine_control(self, routine_id: int, control_type: int, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT, data: Optional[bytes] = None) -> RoutingControlResponseData:
        """Sends a request for RoutineControl

        Args:
            timeout (float): timeout for the UDS operation in seconds
            routine_id (int): The routine ID
            control_type (int): Service subfunction
            data (Optional[bytes], optional): Optional additional data to provide to the server. Defaults to None.

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            RoutingControlResponseData
        """
        request = RoutineControl.make_request(routine_id=routine_id, control_type=control_type, data=data)
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = RoutineControl.interpret_response(response=response)
        return interpreted_response.service_data

    def tester_present(self, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> bool:
        """Sends a request for TesterPresent

        Args:
            timeout (float): timeout for the UDS operation in seconds

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            bool: True if tester preset was accepted successfully. False otherwise
        """
        request = TesterPresent.make_request()
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = TesterPresent.interpret_response(response=response)
        return interpreted_response.service_data.subfunction_echo == 0

    def write_did(self, did: int, value: str, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> bool:
        """Sends a request for WriteDataByIdentifier

        Args:
            timeout (float): timeout for the UDS operation in seconds
            did (int): The data identifier to write
            value (str): the value to write

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            bool: True if WriteDataByIdentifier request sent successfully, False otherwise
        """
        request = WriteDataByIdentifier.make_request(did=did, value=value, didconfig={did: MyAsciiCodec()})
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = WriteDataByIdentifier.interpret_response(response=response)
        return interpreted_response.service_data.did_echo == did
    
    def security_access(self, security_algorithm: Type[SECURITY_ALGORITHM_BASE], timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> bool:
        """Sends a request for SecurityAccess

        Args:
            timeout (float): timeout for the UDS operation in seconds
            security_algorithm (Type[SECURITY_ALGORITHM_BASE]): security algorithm to use for security access

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received
        :raises NegativeResponse: with error code and code name, If negative response was received

        Returns:
            bool: True if security access was allowed to the requested level. False otherwise
        """
        request = SecurityAccess.make_request(level=security_algorithm.seed_subfunction,
                                                                mode=SecurityAccess.Mode.RequestSeed)
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = SecurityAccess.interpret_response(response=response,
                                                                                   mode=SecurityAccess.Mode.RequestSeed)
        
        if all(b == 0 for b in interpreted_response.service_data.seed):
            # all zero seed means that security level is already unlocked
            return True
        
        session_key: bytes = security_algorithm(interpreted_response.service_data.seed)
        request = SecurityAccess.make_request(level=security_algorithm.key_subfunction,
                                                                mode=SecurityAccess.Mode.SendKey,
                                                                data=session_key)
        response = self._send_and_read_response(request=request, timeout=timeout)
        interpreted_response = SecurityAccess.interpret_response(response=response,
                                                                                   mode=SecurityAccess.Mode.SendKey)
        
        return interpreted_response.service_data.security_level_echo == security_algorithm.key_subfunction
    
    def raw_uds_service(self, sid: UdsSid, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT, sub_function: Optional[int] = None, data: Optional[bytes] = None) -> RawUdsResponse:
        """sends raw UDS service request and reads response

        Args:
            sid (UdsSid): Service ID of the request
            timeout (float): timeout for the UDS operation in seconds
            sub_function (Optional[int], optional): The service subfunction. Defaults to None.
            data (Optional[bytes], optional): The service data. Defaults to None.

        :raises RuntimeError: If failed to send the request
        :raises ValueError: If parameters are out of range, missing or wrong type
        :raises NoResponse: If no response was received
        :raises InvalidResponse: with invalid reason, if invalid response has received

        Returns:
            RawUdsResponse: Raw UdsResponse
        """
        if sub_function is not None:
            service = RAW_SERVICES_WITH_SUB_FUNC[sid]
        else:
            service = RAW_SERVICES_WITHOUT_SUB_FUNC[sid]
        request = Request(service=service, subfunction=sub_function, data=data)
        return self._send_and_read_raw_response(request=request, timeout=timeout)

    def _send_and_read_response(self, request: Request, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> RawUdsResponse:
        response = self._send_and_read_raw_response(request=request, timeout=timeout)
        
        if not response.positive:
            raise NegativeResponse(code=response.code, code_name=response.code_name)
        
        return response
    
    def _send_and_read_raw_response(self, request: Request, timeout: float = DEFAULT_UDS_OPERATION_TIMEOUT) -> RawUdsResponse:
        raw_response = None
        for i in range(self.attempts):
            sent_bytes = self.data_link_layer.send(data=request.get_payload(), timeout=timeout)
            if sent_bytes < len(request.get_payload()):
                self.logger.error("Failed to send request")
                raise RuntimeError("Failed to send request")
            
            start = time.time()
            while True:
                now = time.time()
                if (now - start) > timeout:
                    self.logger.debug(f"Timeout reading response for request with SID: {hex(request.service.request_id())}, attempt {i}")
                    break

                raw_response = self.data_link_layer.recv(recv_timeout=timeout)

                if not raw_response:
                    self.logger.debug(f"No response for request with SID: {hex(request.service.request_id())}, attempt {i}")
                    break

                response = RawUdsResponse.from_payload(payload=raw_response)
                if not response.valid:
                    raise InvalidResponse(invalid_reason=response.invalid_reason)
                
                if response.service.response_id() != request.service.response_id():
                    self.logger.debug(f"Got unexpected response: {response.service.get_name()}, request was {request.service.get_name()}, discarding and trying to receive again")
                    raw_response = None
                    continue
                
                if not response.positive and response.code == UdsResponseCode.RequestCorrectlyReceived_ResponsePending:
                    self.logger.debug(f"Got error: {response.code_name}, trying to receive again")
                    continue
                else:
                    return response
            

        if not raw_response:
            raise NoResponse
        
        return response
    
    def _split_dids(self, didlist: Union[int, list[int]], data_bytes: bytes) -> list[RdidDataTuple]:  
        if isinstance(didlist, int):  
            didlist = [didlist]  
    
        dids_values = []  
        next_position = 0
    
        for i, curr_did_int in enumerate(didlist):
            curr_position = data_bytes.find(curr_did_int.to_bytes(length=2, byteorder='big')) if i == 0 else next_position  
            if curr_position == -1:  
                self.logger.warning(f"Unexpected DID: {hex(curr_did_int)}, not found in the data.")  
                continue  
            if i < len(didlist) - 1:  # If it's not the last id  
                next_position = data_bytes.find(didlist[i + 1].to_bytes(length=2, byteorder='big'), curr_position + 2)  
                if next_position == -1:  
                    data = data_bytes[curr_position + 2:]
                else:
                    data = data_bytes[curr_position + 2: next_position]  
            else:  # If it's the last id  
                data = data_bytes[curr_position + 2:]  
    
            dids_values.append(RdidDataTuple(did=curr_did_int, data=data.hex()))  
    
        return dids_values  
