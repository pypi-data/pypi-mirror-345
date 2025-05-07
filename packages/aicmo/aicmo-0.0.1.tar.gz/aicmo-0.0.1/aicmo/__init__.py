from openai import OpenAI, types
from scrapingbee import ScrapingBeeClient
from io import BytesIO
from bs4 import BeautifulSoup
from typing import Union, Any
from base64 import b64decode
from hashlib import sha256
from urllib.parse import urlencode
import numpy as np
import boto3, json, tiktoken, pickle, requests, cv2, re, hmac, os, typesense
from typing import Any

class AICMOClient:
    def __init__(
            self,
            aws_secret_name: str,
            secret_dict: dict = {},
            aws_access_key_id: str = None,
            aws_secret_access_key: str = None,
            aws_region_name: str = "us-east-1",
            aws_s3_bucket: str = None,
            tiktoken_encoding: str = "cl100k_base",
            ts_host: str=None,
            ts_port: int=None,
            ts_api_key: str=None,
        ) -> None:
        """
        Initialize the AICMOClient with AWS credentials and OpenAI model.
        """
        
        # Initialize AWS credentials and S3 bucket
        aws_dict = {x: y for x, y in (("region_name", aws_region_name), ("aws_access_key_id", aws_access_key_id), ("aws_secret_access_key", aws_secret_access_key)) if y}
        # Initialize Secrets from AWS Secrets Manager
        if secret_dict:
            self.secret_dict = secret_dict
        else:
            self.secret_dict = self.load_credentials_from_secrets_manager(aws_secret_name, aws_dict=aws_dict)
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', **aws_dict)
        self.stepfunction_client = boto3.client('stepfunctions', **aws_dict)
        # Initialize AWS S3 bucket and directory
        if aws_s3_bucket:
            self.aws_s3_bucket = aws_s3_bucket
        else:
            self.aws_s3_bucket = self.secret_dict.get('AWS_S3_BUCKET', None)
        
        # Initialize OpenAI client
        openai_dict = {x:self.secret_dict[y] for x,y in (("api_key", "OPENAI_API_KEY"), ("organization", "OPENAI_ORG_KEY")) if self.secret_dict.get(y, None)}
        self.openai_client = OpenAI(**openai_dict)

        # Initialize ScrapingBee client
        self.SCRAPINGBEE_API_KEY = self.secret_dict.get('SCRAPINGBEE_API_KEY', None)
        self.scrapingbee_client = ScrapingBeeClient(api_key=self.SCRAPINGBEE_API_KEY)

        # Initialize Tiktoken client
        self.tiktoken_client = tiktoken.get_encoding(tiktoken_encoding)

        TS_HOST = self.secret_dict.get('TS_HOST', ts_host)
        TS_PORT = self.secret_dict.get("TS_PORT", ts_port)
        TS_API_KEY = self.secret_dict.get("TS_API_KEY", ts_api_key)
        if TS_HOST and TS_PORT and TS_API_KEY:

            self.ts_client = typesense.Client({
                'nodes': [
                    {
                        'host': TS_HOST,
                        'port': TS_PORT,
                        'protocol': self.secret_dict.get("TS_PROTOCOL", 'http')
                    }
                ],
                'api_key': TS_API_KEY,
                "connection_timeout_seconds": self.secret_dict.get("TS_CONNECTION_TIMEOUT_SECONDS", 600)
            })
        else:
            self.ts_client = None

        # Initialize OpenAI model
        self.OPENAI_MODEL = self.secret_dict.get('OPENAI_MODEL', None)

        # Initialize Costing for per APIs
        self.COST = json.loads(self.secret_dict['COST'])

    @staticmethod
    def load_credentials_from_secrets_manager(
            aws_secret_name: str,
            aws_dict: dict = {}
        ) -> dict:
        """
        Load credentials from AWS Secrets Manager.
        """
        try:
            secretsmanager_client = boto3.client('secretsmanager', **aws_dict)
            get_secret_value_response = secretsmanager_client.get_secret_value(SecretId=aws_secret_name)
            return json.loads(get_secret_value_response['SecretString'])
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve secrets: {e}")
        
    def tools_call_gpt(
            self,
            messages: list,
            tools: list,
            tool_name: str,
            tokens: dict=None,
            model: str=None,
            tries: int=5
        ) -> dict:
        """
        Call the GPT model with tools.
        """
        if not tokens:
            tokens = self.get_empty_gpt_tokens()
        if not model:
            model = self.OPENAI_MODEL
        ret_val = {
            "completion": None,
            "status": "failed",
            "tokens": tokens
        }
        for _ in range(tries):
            try:
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tools,
                    tool_choice={"type": "function", "function": {"name": tool_name}}
                )
                tokens = self.get_gpt_tokens(completion, model, tokens)
                ret_val['completion'] = completion
                ret_val['status'] = "success"
                ret_val['tokens'] = self.get_gpt_tokens(completion, model, tokens)
                return ret_val
            except Exception as e:
                ret_val['errors'] = str(e)
                print(e)
        return ret_val
    
    def chat_completion_gpt(
            self,
            messages: list,
            tokens: dict=None,
            model: str=None,
            temperature: int=1,
            tries: int=3
        ) -> dict:
        """
        Call the GPT model for chat completion.
        """
        if not tokens:
            tokens = self.get_empty_gpt_tokens()
        if not model:
            model = self.OPENAI_MODEL
        ret_val = {
            "completion": None,
            "status": "failed",
            "tokens": tokens
        }
        for _ in range(tries):
            try:
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                ret_val['completion'] = completion
                ret_val['status'] = "success"
                ret_val['tokens'] = self.get_gpt_tokens(completion, model, tokens)
                return ret_val
            except Exception as e:
                ret_val['errors'] = str(e)
                print(e)
        return ret_val
    
    def get_empty_gpt_tokens(self) -> dict:
        """
        Initialize an empty dictionary for tokens.
        """
        tokens = {
            "input_cost": 0,
            "output_cost": 0,
            "total_cost": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
        return tokens
    
    def get_gpt_tokens(
            self,
            data: types.chat.chat_completion.ChatCompletion,
            model: str,
            tokens: dict
        ) -> dict:
        """
        Calculate the token usage and cost.
        """
        prompt_tokens = data.usage.prompt_tokens
        completion_tokens = data.usage.completion_tokens
        cost = self.COST.get('openai', {}).get("texts", {}).get(model, {})
        openai_input_cost = cost.get('input', None)
        openai_output_cost = cost.get('output', None)
        if openai_input_cost and openai_output_cost:
            tokens['input_cost'] += prompt_tokens * openai_input_cost
            tokens['output_cost'] += completion_tokens * openai_output_cost
            tokens['total_cost'] = round(tokens['input_cost'] + tokens['output_cost'], 4)
        tokens['prompt_tokens'] += prompt_tokens
        tokens['completion_tokens'] += completion_tokens
        tokens['total_tokens'] += prompt_tokens + completion_tokens
        tokens['openai_input_cost'] = openai_input_cost
        tokens['openai_output_cost'] = openai_output_cost
        return tokens
    
    def s3_upload_pickle(
            self,
            output: Any,
            filename: str,
            aws_s3_dir: str=None,
            event_id: str=None,
            sub_dir: str=None,
            aws_s3_bucket: str=None,
            **kwargs
        ) -> str:
        """
        From any file to a pickle then gets uploaded to S3.
        """
        if not aws_s3_bucket:
            aws_s3_bucket = self.aws_s3_bucket
        s3_key = os.path.join(*[x for x in (aws_s3_dir, event_id, sub_dir, filename) if x])
        pickle_buffer = BytesIO()
        pickle.dump(output, pickle_buffer)
        pickle_buffer.seek(0)
        self.s3_client.upload_fileobj(pickle_buffer, aws_s3_bucket, s3_key)
        return f"https://{aws_s3_bucket}.s3.amazonaws.com/{s3_key}"

    def s3_upload_image(
            self,
            filename: str,
            aws_s3_dir: str=None,
            event_id: str=None,
            sub_dir: str=None,
            filepath_dir: str="/tmp",
            aws_s3_bucket: str=None,
            **kwargs
        ) -> str:
        """
        Upload an image to S3.
        """
        if not aws_s3_bucket:
            aws_s3_bucket = self.aws_s3_bucket
        s3_key = os.path.join(*[x for x in (aws_s3_dir, event_id, sub_dir, filename) if x])
        self.s3_client.upload_file(f"{filepath_dir}/{filename}", aws_s3_bucket, s3_key)
        return f"https://{aws_s3_bucket}.s3.amazonaws.com/{s3_key}"

    def s3_upload_json(
            self,
            data: dict,
            filename: str,
            aws_s3_dir: str=None,
            event_id: str=None,
            sub_dir: str=None,
            aws_s3_bucket: str=None,
            **kwargs
        ) -> str:
        """
        Upload a JSON file to S3.
        """
        if not aws_s3_bucket:
            aws_s3_bucket = self.aws_s3_bucket
        s3_key = os.path.join(*[x for x in (aws_s3_dir, event_id, sub_dir, filename) if x])
        self.s3_client.put_object(
            Bucket=aws_s3_bucket,
            Key=s3_key,
            Body=json.dumps(data, indent=4, ensure_ascii=False),
            ContentType='application/json'  # Optional but recommended
        )
        return f"https://{aws_s3_bucket}.s3.amazonaws.com/{s3_key}"

    def send_error(
            self,
            event: dict,
            tool_name: str,
            tb: str,
            send_error_webhook_url: str=None
        ) -> requests.Response:
        if not send_error_webhook_url:
            send_error_webhook_url = self.secret_dict.get('SEND_ERROR_WEBHOOK_URL', None)
        """
        Send an error message to a Slack webhook.
        """
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"Error in {tool_name} tool"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"Event ID: {event['event_id']}"
                            f"User ID: {event['user_id']}"
                            f"{tb}"
                        )
                    }
                }
            ]
        }
        # Define headers
        headers = {
            "Content-type": "application/json"
        }
        # Send POST request to Slack webhook URL
        return requests.post(send_error_webhook_url, json=payload, headers=headers)

    def limit_text_tokens(
            self,
            text: str,
            max_tokens: int=10000
        ) -> str:
        """
        Limit the number of tokens in a text string.
        """
        tokens = self.tiktoken_client.encode(text)
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
        return self.tiktoken_client.decode(tokens)

    def scrape_scrapingbee_sdk(
            self,
            url: str,
            tries: int=3,
            decode_utf: bool=False,
            timeout: int=30,
            stealth_proxy: bool=False,
            render_js: bool=False,
            soup_convert: bool=True,
            wait_browser: str='load'
        ) -> Union[BeautifulSoup, str, bool]:
        """
        Scrape a webpage using the ScrapingBee SDK.
        """
        params = {
            "wait_browser": wait_browser,
            'timeout': str(timeout*1000)
        }
        if stealth_proxy:
            params['stealth_proxy'] = "true"

        params['render_js'] = str(render_js).lower()
        if url:
            for _ in range(tries):
                try:
                    # print("Website:", url)
                    response = self.scrapingbee_client.get(
                        url,
                        params=params
                    )
                    # print("Status Code:", response.status_code)
                    if response.ok:
                        if decode_utf:
                            content = response.content.decode("utf-8")
                            if soup_convert:
                                return BeautifulSoup(content, 'html.parser')
                            return content
                        content = response.content
                        if soup_convert:
                            return BeautifulSoup(content, 'html.parser')
                        return content
                    elif response.status_code == 500:
                        continue
                    return False
                except Exception as e:
                    print(f"ERROR in SCRAPINGBEE SCRAPE SDK")
                    print(e)

    def scrape_requests(
            self,
            url: str,
            soup_convert: bool=True,
            tries: int=3,
            content_decode: str='utf-8'
        ) -> Union[BeautifulSoup, str]:
        """
        Scrape a webpage using the requests library.
        """
        for _ in range(tries):
            resp = requests.get(url)
            try:
                content = resp.content.decode(content_decode)
            except:
                content = resp.content
            if soup_convert:
                return BeautifulSoup(content, 'html.parser')
            return content
        
    def scrape(
            self,
            url: str,
            soup_convert: bool=True,
            tries: int=3,
            content_length: int=500,
            **kwargs
        ) -> Union[BeautifulSoup, str]:
        """
        Scrape a webpage using the ScrapingBee SDK or requests library.
        """
        content = self.scrape_requests(url, soup_convert=soup_convert, tries=tries)
        if not content or len(content.get_text(" ", strip=True)) < content_length:
            print("ScrapingBee SDK")
            content = self.scrape_scrapingbee_sdk(url, soup_convert=soup_convert, tries=tries, stealth_proxy=True, render_js=True, **kwargs)
        return content
    
    def clean_text(
            self,
            text: str
        ) -> str:
        """
        Clean the text by removing extra spaces, newlines, and tabs.
        """
        text = re.sub('\n+', '\n', text).strip()
        text = re.sub(r'\t+', ' ', text).strip()
        text = re.sub(r' +', ' ', text).strip()
        text = re.sub("\n ", "\n", text).strip()
        return text
    

    def google_search_scrapingbee(
            self,
            query: str,
            search_type: str='classic',
            page: int=1,
            nb_results: int=100,
            device: str='desktop',
            country_code: str='us',
            add_html: bool=False,
            nfpr: bool=False,
            language: str='en',
            take_screenshot: bool=False,
            tries: int=5,
            **kwargs
        ) -> dict:
        """
        Perform a Google search using the ScrapingBee API.
        """
        for _ in range(tries):
            res = requests.get(
                url='https://app.scrapingbee.com/api/v1/store/google',
                params={
                    'api_key': self.SCRAPINGBEE_API_KEY,
                    'search': query,
                    'language': language,
                    "search_type": search_type,
                    "page": page,
                    "nb_results": nb_results,
                    "device": device,
                    "country_code": country_code,
                    "add_html": add_html,
                    "nfpr": nfpr
                },
            )
            if res.ok:
                search_results = res.json()
                if take_screenshot:
                    screenshot_fn =self.screenshot_google_search_scapingbee(search_results['meta_data']['url'], **kwargs)
                    search_results['screenshot_fn'] = screenshot_fn
                return search_results

        
    def screenshot_google_search_scapingbee(
            self,
            url: str,
            uid: str,
            save_path: str="/tmp",
            country_code: str='us',
            screenshot_full_page: bool=False,
            max_height: int=1080,
            addtl_fn: str="-google_search_screenshot",
        ) -> str:
        """
        Take a screenshot of a Google search results page using ScrapingBee.
        """
        params = {
            'custom_google': True,
            'stealth_proxy': True,
            'country_code': country_code,
            'screenshot': True
        }
        if screenshot_full_page:
            params['screenshot_full_page'] = screenshot_full_page
        response = self.scrapingbee_client.get(
            url,
            params=params
        )
        if response.ok:
            
            image_np = np.frombuffer(response.content, dtype=np.uint8)
            image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            if screenshot_full_page:
                addtl_fn += "-full_page"
            else:
                image_cv2 = image_cv2[:max_height, :]
            if addtl_fn:
                filename = f"{uid}{addtl_fn}.png"
            else:
                filename = f"{uid}.png"
            # print("Image shape:", image_cv2.shape)
            # Save the image using OpenCV
            filepath = f"{save_path}/{filename}"
            cv2.imwrite(filepath, image_cv2)
            return {
                "filename": filename,
                "save_path": filepath,
                "viewport": {
                    "width": image_cv2.shape[1], 
                    "height": image_cv2.shape[0]
                }
            }

    def screenshot_webpage(
            self,
            url: str,
            uid: str,
            idx: str,
            save_path: str="/tmp",
            tries: int=3
        ) -> list:
        """
        Take a screenshot of a webpage using the ScrapingBee API.
        """
        os.makedirs(save_path, exist_ok=True)
        for _ in range(tries):
            response2 = self.scrapingbee_client.get(
                url,
                params={
                    'wait': '5000',
                    'stealth_proxy': True,
                    'country_code': 'us',
                    "wait_browser": "networkidle0",
                    'screenshot_full_page': True,
                    "json_response":True,
                    "render_js": True,
                    'js_scenario': {
                        "instructions": [
                            {"wait": 1000},
                            {"infinite_scroll": # Scroll the page until the end
                                {
                                    "max_count": 0, # Maximum number of scroll, 0 for infinite
                                    "delay": 1000, # Delay between each scroll, in ms
                                    # "end_click": {"selector": "#button_id"} # (optional) Click on a button when the end of the page is reached, usually a "load more" button
                                }
                            }
                        ]
                    }
                }
            )
            if response2.ok:
                res2_json = response2.json()
                return self.crop_images(res2_json['screenshot'], uid, idx, save_path)
        return []

    def get_render_link_urlbox(
            self,
            args: dict
        ) -> str:
        """
        Generate a render link for URLBox API.
        """
        URLBOX_API_SECRET = self.secret_dict.get('URLBOX_API_SECRET', None)
        URLBOX_API_KEY = self.secret_dict.get('URLBOX_API_KEY', None)
        queryString = urlencode(args, True)
        hmacToken = hmac.new(str.encode(URLBOX_API_SECRET), str.encode(queryString), sha256)
        token = hmacToken.hexdigest().rstrip('\n')
        return "https://api.urlbox.com/v1/%s/%s/png?%s" % (URLBOX_API_KEY, token, queryString)
 
    def screenshot_webpage_urlbox(
            self,
            url: str,
            uid: str,
            idx: str,
            width: int=1920,
            height: int=1080,
            format: str="png",
            full_page: bool=True,
            save_path: str="/tmp",
            full_page_mode: str="stitch",
            click_accept: bool=True,
            press_escape: bool=True,
            block_ads: bool=True,
            hide_cookie_banners: bool=True,
            delay: Union[str, int]="5000",
            scroll_delay: Union[str, int]="200",
            scroll_increment: Union[str, int]="200",
            wait_until: str="requestsfinished",
            engine_version: str="stable",
            user_agent: str="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            tries: int=3
        ) -> list:
        os.makedirs(save_path, exist_ok=True)
        """
        Take a screenshot of a webpage using the URLBox API.
        """
        d = {
            "format": format,
            "url": url,
            "width": width,
            "height": height,
            "full_page": full_page,
            "full_page_mode": full_page_mode,
            "click_accept": click_accept,
            "press_escape": press_escape,
            "block_ads": block_ads,
            "hide_cookie_banners": hide_cookie_banners,
            "delay": delay,
            "wait_until": wait_until,
            "scroll_delay": scroll_delay,
            "engine_version": engine_version,
            "scroll_increment": scroll_increment,
            "user_agent": user_agent
        }
        for _ in range(tries):
            render_link = self.get_render_link_urlbox(d)
            response = requests.get(render_link)
            
            if response.ok:
                return self.crop_images(response.content, uid, idx, save_path)
        return []

    def get_bytes_or_b64decoded(
            self,
            data: Union[bytes, str]
        ) -> bytes:
        """
        Convert base64-encoded string to bytes or return bytes as is.
        """
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return b64decode(data)  # Let it raise if it's not valid base64 or not ASCII
        else:
            raise TypeError("Input must be bytes or base64-encoded string.")

    def crop_images(
            self,
            img_data: bytes,
            uid: str,
            idx: str,
            save_path: str,
            max_h: int = 2048,
            max_w: int = 2048,
            screenshots = [],
            page_length: int = 10,
        ) -> list:
        """
        Crop images from the screenshot data.
        """
        img_data = self.get_bytes_or_b64decoded(img_data)
        image_np = np.frombuffer(img_data, dtype=np.uint8)
        image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        curr_h = max_h
        prev_h = 0
        im_h = image_cv2.shape[0]
        c = 1
        b = False
        for _ in range(page_length):
            im_cropped = image_cv2[prev_h:curr_h, :max_w]
            if im_cropped.size:
                im_cropped_shape = im_cropped.shape
                print("im_cropped.shape:", im_cropped.shape)
                fn = f"{uid}-{idx}-{c}.png"
                sp = f"{save_path}/{fn}"
                screenshots.append({"save_path": sp, "filename": fn, "viewport": {"width": im_cropped_shape[1], "height": im_cropped_shape[0]}})
                print("save_path:", sp)
                cv2.imwrite(sp, im_cropped)
            else:
                b = True
            if b: return screenshots
            elif curr_h+max_h > im_h:
                prev_h = curr_h
                curr_h = im_h
                b = True
            else:
                prev_h = curr_h
                curr_h += max_h
            c += 1
        return screenshots
    
    def ts_semantic_search(
            self,
            query: str, 
            collection_name: str = None, 
            distance_threshold: float = 0.8,
            limit: int = 5, 
            filter_by: str = None,
            query_by: list = ['contents', 'embedding'],
            exclude_fields: list = ['embedding'],
            query_by_weights: list = [2, 1],
            top_k: int = 200,
            prioritize_exact_match: bool = True,
            num_typos: int=0,
            prefix = False,
            **kwargs: Any
        ) -> list:
        """
        Perform a semantic search using Typesense.
        """
        if not collection_name:
            collection_name = self.secret_dict.get('TS_COLLECTION_NAME', None)

        search_params = {
            # 'query_by': ",".join(query_by),
            # 'query_by_weights': ",".join([str(x) for x in query_by_weights]),
            'q': query,
            "prefix": prefix,
            "prioritize_exact_match": prioritize_exact_match,
            "limit": limit,
            "num_typos": num_typos,
        }
        if not query_by:
            raise ValueError("query_by must be provided")
        else:
            if len(query_by) == 1:
                search_params['query_by'] = query_by[0]
            else:
                if len(query_by) != len(query_by_weights):
                    raise ValueError("query_by and query_by_weights must have the same length")
                else:
                    search_params['query_by'] = ",".join(query_by),
                    search_params['query_by_weights'] = ",".join([str(x) for x in query_by_weights]),

        if exclude_fields:
            search_params['exclude_fields'] = ",".join(exclude_fields)
        if distance_threshold:
            search_params['vector_query'] = f"embedding:([], k: {top_k}, distance_threshold: {distance_threshold})"
        if filter_by:
            search_params['filter_by'] = filter_by
        # print(json.dumps(search_params, indent=4, ensure_ascii=False))
        return self.ts_client.collections[collection_name].documents.search(search_params)
    

    def ts_upsert_data(
            self,
            data: dict, 
            collection_name: str= None
        ) -> None:
        """
        Upsert data into Typesense collection.
        """
        if not collection_name:
            collection_name = self.secret_dict.get('TS_COLLECTION_NAME', None)
        self.ts_client.collections[collection_name].documents.upsert(data)

    def research(
            self,
            user_input: str,
            url: str = None,
            instructions: str = None,
            score_thresh: int = 7,
            **kwargs
        ):
        if url is None:
            resp = self.google_search_scrapingbee(user_input)
            resp_json = resp.json()

            for res in resp_json['organic_results']:
                # res = resp_json['organic_results'][0]
                desc = res['description']
                title = res['title']
                domain = res['domain']

                webpage_desc = f'{title} - {domain}\n\n{desc}'

                messages = [
                    {
                        "role": "system",
                        "content": f'''Compare the following two texts and determine their similarity. The first text is the user input, and the second text is a webpage description. Analyze whether the user input conveys a meaning, topic, or key ideas similar to the webpage description, even if the wording is different. Provide a similarity score from 0 to 10, with 10 being identical and 0 being completely unrelated. Additionally, highlight key matching themes, topics, or phrases.
                User input: {user_input}
                Webpage Description: {webpage_desc}'''
                    }
                ]

                text_similarity_tool_name = "text_similarity_tool"
                text_similarity_schema = [
                    {
                        "type": "function",
                        "function": {
                            "name": text_similarity_tool_name,
                            "strict": True,
                            "description": "Compares two texts to determine their similarity. The first text is user input, and the second is a webpage description. The function analyzes whether the user input conveys a meaning, topic, or key ideas similar to the webpage description, even if the wording differs. It returns a similarity score from 0 to 10, where 10 means identical and 0 means completely unrelated.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "score": {
                                        "type": "number",
                                        "description": "A similarity score between 0 and 10, where 10 means the texts are identical in meaning, and 0 means they are completely unrelated.",
                                    },
                                    "reason": {
                                        "type": "string",
                                        "description": "A brief explanation of why the given similarity score was assigned, highlighting key matching themes, topics, or differences.",
                                    }
                                },
                                "required": ["score", "reason"],
                                "additionalProperties": False
                            },
                        }
                    }
                ]

                retval = self.tools_call_gpt(
                            messages=messages,
                            tool_choice={"type": "function", "function": {"name": text_similarity_tool_name}},
                            tools=text_similarity_schema,
                        )

                arguments = json.loads(retval.choices[0].message.tool_calls[0].function.arguments)
                score = arguments['score']
                reason = arguments['reason']
                
                print("score:", score)
                print("reason:", reason)
                print("domain:", domain)
                print("title:", title)
                print("desc:", desc)
                print()
                print("*"*100)
                print()

                if score >= score_thresh:
                    url = res['url']
                    break
        if url:
            soup = self.scrape_requests(url)
            if not soup:
                soup = self.scrape_scrapingbee_sdk(url)
            clean_website_text = self.clean_text(soup.text)
            # print(clean_website_text)
            if instructions:
                content = f"Follow these instructions: '{instructions}'. Ensure the output meets the specified format or requirements while maintaining accuracy and clarity. If relevant data is unavailable, provide a reasonable alternative or explanation.\n\nScraped Website's Data:{clean_website_text}"
            else:
                content = f"Summarize the key content of the following scraped webpage based on the user's input. Focus on the aspects most relevant to what the user is asking for, ensuring the summary aligns with their query. Highlight the main topics, key points, and any important details related to the user's intent. If applicable, emphasize notable features, services, or unique aspects relevant to their request.\n\nUser Input: {user_input}\n\nScraped Website Text:\n{clean_website_text}"
            print(content)
            messages2 = [
                {
                    "role": "system",
                    "content": content
                }
            ]
            retval2 = self.chat_completion_gpt(messages2)
            result = retval2.choices[0].message.content
            result += f"\n\nSource(s): {url}"
        else:
            messages2 = [
                {
                    "role": "system",
                    "content": f"Tell the user that there's no available data based on their search input: '{user_input}'. Instead, provide an insightful response related to their query using general knowledge, context, and reasoning to help address their question as best as possible."
                }
            ]
            retval2 = self.chat_completion_gpt(messages2)
            result = retval2.choices[0].message.content
        return {
            "type": "string",
            "value": result
        }