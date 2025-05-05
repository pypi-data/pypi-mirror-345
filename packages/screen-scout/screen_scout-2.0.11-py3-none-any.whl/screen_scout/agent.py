import boto3
import json
from test_creation_util import get_all_links
from typing import List
from pydantic import BaseModel
import uuid
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, Controller
import asyncio
from dotenv import load_dotenv
from browser_use.browser.context import BrowserContext, BrowserContextConfig

load_dotenv()


class TestCase(BaseModel):
    testName: str
    testType: str
    description: str
    steps: List[str]
    expectedResult: str
    url: str


class TestCases(BaseModel):
    testCase: List[TestCase]


class TestResult(BaseModel):
    testName: str
    description: str
    steps: List[str]
    result: str
    notes: str


def send_file_to_s3(path, value):
    aws_access_key = "AKIAWCA4TSYCS3BEU4UF"
    aws_secret_key = "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"
    aws_region = "us-east-1"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    bucket_name = "screenscout-videos"
    video_file_path = path
    s3_key = f"videos/{value}.webm"  # Path in S3

    try:
        s3.upload_file(video_file_path, bucket_name, s3_key)
        # print(f"Video uploaded successfully to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading video: {e}")


def upload_dict_to_s3(data_dict, video_id, url):

    bucket_name = "screenscout-videos"
    aws_access_key = "AKIAWCA4TSYCS3BEU4UF"
    aws_secret_key = "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"
    aws_region = "us-east-1"
    s3_key = f"past_runs/{url}/{video_id}.json"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    json_content = json.dumps(data_dict, indent=4)

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json_content,
            ContentType="application/json"
        )
        print(
            f"JSON file uploaded successfully to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading JSON file: {e}")


async def generate_tests_for_link(new_prompt, link, key):
    controller = Controller(output_model=TestCases)
    config = BrowserContextConfig(
        highlight_elements=True
    )

    browser = Browser(config=BrowserConfig(headless=True))
    context = BrowserContext(browser=browser, config=config)

    agent = Agent(
        browser_context=context,
        task=new_prompt,
        llm=ChatOpenAI(model="gpt-4o", api_key=key),
        controller=controller,
        generate_gif=False
    )
    result = await agent.run(max_steps=5)

    result = result.final_result()
    await browser.close()
    await context.close()
    if isinstance(result, str):
        import json
        try:
            json_res = json.loads(result)
            result_dict = {}
            result_dict['output'] = json_res
            return result_dict
        except json.JSONDecodeError:
            return {"error": "Invalid JSON string"}

    return result


class TestingAgent:
    def __init__(self, name):
        self.name = name

    async def create_custom_test(self, prompt: str, key: str):
        controller = Controller(output_model=TestCases)
        config = BrowserContextConfig(
            highlight_elements=True
        )

        browser = Browser(config=BrowserConfig(headless=True))
        context = BrowserContext(browser=browser, config=config)

        agent = Agent(
            browser_context=context,
            task=prompt,
            llm=ChatOpenAI(model="gpt-4o", api_key=key),
            controller=controller,
            generate_gif=False
        )
        result = await agent.run(max_steps=5)

        result = result.final_result()
        await browser.close()
        await context.close()
        if isinstance(result, str):
            import json
            try:
                json_res = json.loads(result)
                result_dict = {}
                result_dict['output'] = json_res
                return result_dict
            except json.JSONDecodeError:
                return {"error": "Invalid JSON string"}

        return result

    async def execute_comprehensive_test(self, test_number: int, test_description: str, test_depth: int, key: str, url: str):
        is_test_execution = True if 'You are an expert QA engineer' not in test_description else False
        if not is_test_execution:
            website_url = url
            links = get_all_links(base_url='https://' +
                                  website_url, max_links=test_depth)
            result = {'output': {"testCase": []}}
            tasks = []
            for link in links:
                tasks.append(generate_tests_for_link(
                    test_description.replace(website_url, link), link, key))

            results = await asyncio.gather(*tasks)
            for res in results:
                try:
                    result['output']['testCase'].extend(
                        res['output']['testCase'])
                except:
                    print("JSON FORMAT ISSUE")
                    pass
        else:
            video_path = str(uuid.uuid4())
            controller = Controller(output_model=TestResult)
            config = BrowserContextConfig(
                save_recording_path=f"./videos/{str(video_path)}",
                highlight_elements=True
            )

            browser = Browser(config=BrowserConfig(headless=True))
            context = BrowserContext(browser=browser, config=config)

            agent = Agent(
                browser_context=context,
                task=test_description,
                llm=ChatOpenAI(model="gpt-4o-mini", api_key=key),
                controller=controller,
                generate_gif=False
            )
            result = await agent.run(max_steps=15)
            result = result.final_result()

            await browser.close()
            await context.close()

            if isinstance(result, str):
                import json
                try:
                    json_res = json.loads(result)
                    result_dict = {}
                    result_dict[test_number] = json_res
                    if is_test_execution:
                        result_dict['video_id'] = video_path
                        result_dict['url'] = url
                    return result_dict
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON string"}
        return result
