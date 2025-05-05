import requests
import jwt
import time
from typing import Optional
from urllib.parse import urlencode
import yaml


class EizenSDK:
    def __init__(
        self,
        refresh_token: str,
        access_token: str,
        # base_url: str = "https://vip-dev-api.eizen.ai/analytics/v1",
        # keycloak_base_url: str = "https://keycloak-dev.eizen.ai",
        # client_id: str = "analytics-service",
        # gateway_base_url: str = "https://gateway-dev.eizen.ai"
        base_url: str = "https://backend.eizen.ai/analytics/v1",
        keycloak_base_url: str = "https://keycloak.analytics.eizen.ai",
        client_id: str = "analytics-service",
        gateway_base_url: str = "https://gateway-ldev.eizen.ai"
    ):
        self.__refresh_token = refresh_token
        self.base_url = base_url
        self.keycloak_base_url = keycloak_base_url
        self.client_id = client_id
        self.gateway_base_url = gateway_base_url
        self.__tenant_id = 0
        self.__access_token = None
        self.__fetch_access_token()
        self.__get_tenant_id()
        self.access_token = access_token

    def __fetch_access_token(self):
        """Fetch a new access token using the refresh token."""
        if not self.__refresh_token or self.__is_token_expired(self.__refresh_token):
            raise Exception("Refresh token is expired. Please provide a new one.")

        url = f"{self.keycloak_base_url}/realms/Analytics/protocol/openid-connect/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.__refresh_token,
        }

        response = requests.post(
            url,
            data=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            tokens = response.json()
            self.__access_token = tokens["access_token"]
            self.__refresh_token = tokens.get("refresh_token", self.__refresh_token)
        else:
            raise Exception(f"Failed to retrieve access token: {response.text}")

    def __refresh_access_token(self):
        """Refresh the access token using the refresh token."""
        if not self.__refresh_token or self.__is_token_expired(self.__refresh_token):
            self.__fetch_new_tokens()  # If refresh token expired, get new tokens
            return

        url = f"{self.keycloak_base_url}/realms/Analytics/protocol/openid-connect/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.__refresh_token,
        }

        response = requests.post(
            url,
            data=urlencode(data),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            tokens = response.json()
            self.__access_token = tokens["access_token"]
            self.__refresh_token = tokens.get("refresh_token", self.__refresh_token)
        else:
            self.__fetch_new_tokens()  # If refresh fails, fetch new tokens

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing it if necessary."""
        if not self.__access_token or self.__is_token_expired(self.__access_token):
            self.__fetch_access_token()
        return self.__access_token

    def __is_token_expired(self, token: str) -> bool:
        """Check if a JWT token is expired."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload["exp"] < time.time()
        except Exception as e:
            return True  # If token is invalid, assume expired

    def __make_request(self, method: str, url: str, **kwargs):
        """Handles API requests and refreshes token if needed."""
        if self.__is_token_expired(self.__access_token):
            self.__refresh_access_token()

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.__access_token}"
        kwargs["headers"] = headers

        response = requests.request(method, url, **kwargs)

        if response.status_code == 401:
            self.__refresh_access_token()
            headers["Authorization"] = f"Bearer {self.__access_token}"
            response = requests.request(method, url, **kwargs)

        if response.status_code // 100 != 2:
            raise Exception(f"Request failed ({response.status_code}): {response.text}")
        
        if response.status_code == 204:
            return {} 
        
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
        
        return response.text

    def __make_request_access_token(self, method: str, url: str, **kwargs):
        """Handles API requests and refreshes token if needed."""
        if self.__is_token_expired(self.__access_token):
            self.__refresh_access_token()

        headers = kwargs.get("headers", {})
        headers["access_token"] = self.access_token
        kwargs["headers"] = headers
        print(headers)
        response = requests.request(method, url, **kwargs)

        if response.status_code == 401:
            self.__refresh_access_token()
            headers["access_token"] = self.access_token  # Keep consistent lowercase
            response = requests.request(method, url, **kwargs)

        if response.status_code // 100 != 2:
            raise Exception(f"Request failed ({response.status_code}): {response.text}")
        
        if response.status_code == 204:
            return {} 
        
        if response.headers.get("Content-Type") == "application/json":
            return response.json()
        
        return response.text 

    def __get_tenant_id(self):
        
        payload = jwt.decode(self.__access_token, options={"verify_signature": False})
        self.username = payload["preferred_username"]

        url = f"{self.base_url}/user"
        self.__tenant_id = self.__make_request(
            "GET", url, params={"email": self.username}
        )["tenantId"]

    def get_analytics(self):
        url = f"{self.base_url}/analytics/tenant/{self.__tenant_id}"
        analytics = self.__make_request("GET", url)
        return [{"id": i["id"], "name": i["name"]} for i in analytics]

    def get_analytic_zones(self, analytic_id: int):
        url = f"{self.base_url}/zone/analytics/{analytic_id}"
        zones = self.__make_request("GET", url)
        return [{"id": i["id"], "name": i["name"]} for i in zones]

    def get_zone_sources(self, zone_id: int):
        url = f"{self.base_url}/source/zone/{zone_id}"
        sources = self.__make_request("GET", url)
        return [{"id": i["id"], "name": i["name"]} for i in sources]

    def get_analytic_sources(self, analytic_id: int):
        url = f"{self.base_url}/source/analytics/{analytic_id}"
        sources = self.__make_request("GET", url)
        return [{"id": i["id"], "name": i["name"]} for i in sources["sources"]]

    def get_source_details(self, source_id: int):
        url = f"{self.base_url}/source/{source_id}"
        return self.__make_request("GET", url)

    def get_source_summary(self, source_id: int):
        url = f"{self.base_url}/videos/summary/{source_id}"
        return self.__make_request("GET", url)

    def get_models(self):
        url = f"{self.base_url}/model/tenant/{self.__tenant_id}"
        models = self.__make_request("GET", url)
        return [{"id": i["id"], "name": i["name"]} for i in models]






    def get_all_tenants(self):
        url = f"{self.base_url}/tenant"
        tenants = self.__make_request("GET", url)
        return tenants
    
    def get_all_analytics(self):
        url = f"{self.base_url}/analytics"
        analytics = self.__make_request("GET", url)
        return analytics
    
    def add_tenant(self,name, iconUri="https://example.com/acme_logo.png"):
        payload = {"name":name,"iconUri":iconUri}
        url = f"{self.base_url}/tenant"
        tenant = self.__make_request("POST",url,json=payload)
        return tenant

    def add_analytics(self, name, description, tenant_id, analytics_type_id, analytics_category_id,iconUri="https://example.com/acme_logo.png"):
        payload = {
            "name": name,
            "description": description,
            "iconUri": iconUri,
            "tenantId": tenant_id,
            "analyticsTypeId": analytics_type_id,
            "analyticsCategoryId": analytics_category_id
        }
        url = f"{self.base_url}/analytics"
        analytics = self.__make_request("POST", url, json=payload)
        return analytics
    
    def add_analytics_type(self, name, description, tenant_id,icon_uri="https://example.com/acme_logo.png"):
        payload = {
            "name": name,
            "description": description,
            "iconUri": icon_uri,
            "tenantId": tenant_id
        }
        url = f"{self.base_url}/analytics-type"
        analytics_type = self.__make_request("POST", url, json=payload)
        return analytics_type

    def add_analytics_category(self, name, description, tenant_id, analytics_type_id, icon_uri="https://example.com/acme_logo.png"):
        payload = {
            "name": name,
            "description": description,
            "iconUri": icon_uri,
            "tenantId": tenant_id,
            "analyticsTypeId": analytics_type_id
        }
        url = f"{self.base_url}/analytics-category"
        analytics_category = self.__make_request("POST", url, json=payload)
        return analytics_category



    def get_analytics_type(self, analytics_type_id):
        url = f"{self.base_url}/analytics-type/{analytics_type_id}"
        analytics_type = self.__make_request("GET", url)
        return analytics_type


    def get_analytics_category(self, analytics_category_id):
        url = f"{self.base_url}/analytics-category/{analytics_category_id}"
        analytics_category = self.__make_request("GET", url)
        return analytics_category
    
        

    def get_all_analytics_types(self):
        url = f"{self.base_url}/analytics-type"
        analytics_types = self.__make_request("GET", url)
        return analytics_types

    def get_all_analytics_categories(self):
        url = f"{self.base_url}/analytics-category"
        analytics_categories = self.__make_request("GET", url)
        return analytics_categories
    

    def get_all_zones(self):
        url = f"{self.base_url}/zone"
        zones = self.__make_request("GET", url)
        return zones

    def get_zone(self, zone_id):
        url = f"{self.base_url}/zone/{zone_id}"
        zone = self.__make_request("GET", url)
        return zone

    def add_zone(self, name, analytics_id):
        payload = {
            "name": name,
            "analyticsId": analytics_id
        }
        url = f"{self.base_url}/zone"
        zone = self.__make_request("POST", url, json=payload)
        return zone

    def get_all_models(self):
        url = f"{self.base_url}/model"
        models = self.__make_request("GET", url)
        return models

    def add_model(self, name, description, model_type,system,model_cd,model_category, objects, events, activities, endpoint_url, tenants, use_cases, is_inference_active, image_url="https://example.com/acme_logo.png",
                  anomalies=[]):
        payload = {
            # --- Fields from the new CreateModel ---
            "name": name,                             # String
            "modelCd": model_cd,                       # String or None (maps to String?)
            "system": system,                         # String or None (maps to String?)
            "modelCategory": model_category,             # String or None (maps to String?)
            "anomalies": anomalies,                   # List[str] (maps to List<String>)
            "description": description,               # String
            "modelType": model_type,                  # String
            "objects": objects,                       # List[str] (maps to List<String>)
            "events": events,                         # List[str] (maps to List<String>)
            "activities": activities,                 # List[str] (maps to List<String>)
            "imageUrl": image_url,                    # String
            "endpointUrl": endpoint_url,              # String
            "tenants": tenants,                       # List[int] (maps to List<Long>)
            "useCases": use_cases,                    # List[str] (maps to List<String>)
            "isInferenceActive": is_inference_active, # bool (maps to Boolean)
        }
        url = f"{self.base_url}/model"
        model = self.__make_request("POST", url, json=payload)
        return model

    def get_all_users(self):
        url = f"{self.base_url}/user/list" 
        analytics_types = self.__make_request("GET", url)
        return analytics_types

    def create_user(self, user_name, email, password, first_name, last_name, roles, tenant_id, analytics_id):
        """
        Creates a new user via the API.

        Args:
            user_name (str): Username for the new user.
            email (str): Email address for the new user.
            password (str): Password for the new user.
            first_name (str): First name of the user.
            last_name (str): Last name of the user.
            roles (list[str]): List of role strings to assign.
            tenant_id (int): The ID of the tenant the user belongs to.
            analytics_id (list[int]): List of analytics IDs associated with the user.

        Returns:
            dict: The created user object returned by the API.
                  Raises an exception if the request fails.
        """

        payload = {
            "userName": user_name,
            "email": email,
            "password": password,
            "firstName": first_name,
            "lastName": last_name,
            "roles": roles,
            "tenantId": tenant_id,
            "analyticsId": analytics_id
        }
        url = f"{self.base_url}/user"
        user = self.__make_request("POST", url, json=payload)
        return user

    def create_source(
        self,
        name: str,
        username: str,
        password: str,
        source_url: str,
        description: str,
        source_type: str,
        zone_id: int,
        mongo_host: str,
        mongo_db: str,
        models: list,
    ):
        url = f"{self.base_url}/source"
        return self.__make_request(
            "POST",
            url,
            json={
                "name": name,
                "userName": username,
                "password": password,
                "sourceUrl": source_url,
                "description": description,
                "sourceType": source_type,
                "zoneId": zone_id,
                "mongoHost": mongo_host,
                "mongoDb": mongo_db,
                "models": models,
            },
        )

    def create_sources_from_yaml(self, yaml_file: str):
        """
        Reads a YAML file containing a list of sources and calls create_source for each entry.

        :param yaml_file: Path to the YAML file containing source definitions.
        """
        with open(yaml_file, "r") as file:
            sources = yaml.safe_load(file)

        if not isinstance(sources, list):
            raise ValueError("YAML file must contain a list of sources.")

        response = []

        for source in sources:
            response.append(
                self.create_source(
                    name=source["name"],
                    username=source["username"],
                    password=source["password"],
                    source_url=source["source_url"],
                    description=source["description"],
                    source_type=source["source_type"],
                    zone_id=source["zone_id"],
                    mongo_host=source["mongo_host"],
                    mongo_db=source["mongo_db"],
                    models=source.get(
                        "models", []
                    ),  # Default to empty list if models key is missing
                )
            )

        return [i["id"] for i in response]

    def delete_source(self, source_id: int):
        url = f"{self.base_url}/source/{source_id}"
        return self.__make_request("DELETE", url)
    

    def yolo_inference(
        self,
        model_id: int,
        input_type: str,
        media_url: str,
        response_type: str,
        s3_bucket_name: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None,
    ):

        # Get model details first
        url = f"{self.base_url}/model/{model_id}"
        model = self.__make_request("GET", url)
        endpoint = model["endpointUrl"]
        inferenceUrl = f"{self.gateway_base_url}/ez_yolo_model_inference/"


        # Send inference data
        data = {
            "inferenceUrl": endpoint,
            "inputType": input_type,
            "media_url": media_url,
            "responseType": response_type,
            "s3AccessKey": s3_access_key,
            "s3Secretkey": s3_secret_key,
            "s3BucketName": s3_bucket_name,
        }
        headers = {"access_token": self.access_token}
        return self.__make_request_access_token("POST", inferenceUrl, json=data, headers=headers)

    def collect_data(
        self,
        source_id: int,
        time_interval: int = 10,
        number_of_frames_requested: int = None,
        skip_frame_count: int = None,
        s3_bucket_name: str = None,
        s3_access_key: str = None,
        s3_secret_key: str = None,
        s3_cloud_path: str = None,
    ):
        url = f"{self.gateway_base_url}/ez_collect-data-to-label-studio/"

        headers = {"access_token": self.access_token}

        if number_of_frames_requested:
            time_interval = None
        data = {
            "id": source_id,
            "s3_access_key": s3_access_key,
            "s3_secret_key": s3_secret_key,
            "s3_bucket_name": s3_bucket_name,
            "s3_cloud_folder_path": s3_cloud_path,
            "time_interval": time_interval,
            "number_of_frames_requested": number_of_frames_requested,
            "skip_frame_count": skip_frame_count,
        }

        return self.__make_request_access_token("POST", url, json=data, headers=headers)


    def model_building(
        self,
        modelName: Optional[str] = None,
        modelCategory: Optional[str] = None,
        modelType: Optional[str] = "private",
        modelWeightsPath: Optional[str] = "",
        dataPath: Optional[str] = "",
        numberOfEpochs: Optional[int] = 50,
        useWeights: Optional[bool] = False,
        yaml_file: Optional[str] = None
        ):
        try:
            url = f"{self.gateway_base_url}/ez_model_training/"
            
            if yaml_file:
                with open(yaml_file, "r") as file:
                    modelData = yaml.safe_load(file)

                if not isinstance(modelData, list):
                    raise ValueError("YAML file must contain a list of sources.")

                if modelData:
                    data = modelData[0]
                    modelName = data.get('modelName')
                    modelCategory = data.get('modelCategory')
                    modelWeightsPath = data.get('modelWeightsPath', "")
                    dataPath = data.get('dataPath', "")
                    useWeights = data.get('useWeights', False)
                    numberOfEpochs = data.get('numberOfEpochs', 10)


            data = {
                "modelName": modelName,
                "modelType": modelType,
                "modelCategory": modelCategory,
                "dataPath": dataPath,
                "modelWeightsPath": modelWeightsPath,
                "numberOfEpochs": numberOfEpochs,
                "useWeights": useWeights
            }

            headers = {"access_token": self.access_token}
            model_building = self.__make_request_access_token("POST", url, json=data, headers=headers)
            return model_building
        
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except FileNotFoundError:
            print(f"File not found: {yaml_file}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


    def model_retraining(
        self,
        id: Optional[int] = None,
        modelType: Optional[str] = "private",
        dataPath: Optional[str] = None,
        useWeights : Optional[bool] = True,
        numberOfEpochs: Optional[int] = 50,
        yaml_file: Optional[str] = None
        ):
        try:
            url = f"{self.gateway_base_url}/ez_model_retraining/"

            if yaml_file:
                with open(yaml_file, "r") as file:
                    modelData = yaml.safe_load(file)

                if not isinstance(modelData, list):
                    raise ValueError("YAML file must contain a list of sources.")

                if modelData:
                    data = modelData[0]
                    id = data.get('id')
                    modelType = data.get('modelType', "private")
                    dataPath = data.get('dataPath', "")
                    useWeights = data.get('useWeights', True)
                    numberOfEpochs = data.get('numberOfEpochs', 10)

            headers = {"access_token": self.access_token}
            model_retraining_data = {
                    "id": id,
                    "modelType": modelType,
                    "dataPath": dataPath,
                    "numberOfEpochs": numberOfEpochs,
                    "useWeights": useWeights
                }


            model_retraining = self.__make_request_access_token("POST", url, json=model_retraining_data, headers=headers)
            return model_retraining
    
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
        except ValueError as e:
            print(f"Value error: {e}")
        except FileNotFoundError:
            print(f"File not found: {yaml_file}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def video_process_llava(
        self,
        videoUrl: str,
        instruction: str,
        version: Optional[str] = None,
        modelID: Optional[str] = "EZA_MDL_FOUN_LLAV_NEXT_VIDEO"
    ):
        url = f"{self.gateway_base_url}/ez_video_process_llava_video/"
        print("Video Process Strated .....")
        data = {
            "videoFile": videoUrl,
            "instruction": instruction,
            "version": version,
            "modelID": modelID
        }
        print(data)
        headers = {"access_token": self.access_token}
        video_process = self.__make_request_access_token("POST", url, json=data, headers=headers)
        return video_process