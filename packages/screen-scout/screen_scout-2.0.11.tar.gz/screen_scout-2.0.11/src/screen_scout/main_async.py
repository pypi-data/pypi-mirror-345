import argparse
import asyncio
import json
import time
from typing import List, Optional
from .templates import (
    create_test_template_comprehensive,
    create_custom_test_template,
    execute_test_template,
)
from .testing_agent import TestingAgent, format_steps, run_comprehensive_test


async def main(
    argv: Optional[List[str]] = None,
    *,
    return_results: bool = False,
) -> Optional[List[dict]]:
    """
    Single entry‑point for *all* modes:
      --comprehensive      crawl several links and create+run tests
      --test-description   generate tests from a requirement, then run them
      --execute            run exactly one prompt you already wrote
    """
    parser = argparse.ArgumentParser(prog="screen‑scout")
    parser.add_argument("--url", required=True)
    parser.add_argument("--key", default="")
    parser.add_argument("--port", type=int, default=3000)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--comprehensive", action="store_true")
    group.add_argument("--test-description")
    group.add_argument("--execute")

    parser.add_argument("--num-tests", type=int, default=1)
    parser.add_argument("--test-depth", type=int, default=4)
    parser.add_argument("--record", action="store_true")

    args = parser.parse_args(argv)

    # ------------------------------------------------------------------ #
    # 1 Generate a list[tuple] -> (name, prompt, depth, key, url)
    # ------------------------------------------------------------------ #
    test_inputs = []

    if args.comprehensive:
        prompt = (
            create_test_template_comprehensive
            .replace("{{.webURL}}", args.url)
            .replace("{{.ntype}}", str(args.num_tests))
        )
        test_inputs.append(
            ("Comprehensive", prompt, args.test_depth, args.key, args.url))

    elif args.test_description:
        prompt = (
            create_custom_test_template
            .replace("{{user_requirement}}", args.test_description)
            .replace("{{.webURL}}", args.url)
            .replace("{{.ntype}}", str(args.num_tests))
        )
        # generate test cases first, then build execution prompts
        agent = TestingAgent("Generator")
        gen = await agent.create_custom_test(prompt, args.key)
        for i, tc in enumerate(gen["output"]["testCase"], 1):
            exec_prompt = (
                execute_test_template
                .replace("{url}", tc["url"])
                .replace("{testName}", tc["testName"])
                .replace("{testType}", tc["testType"])
                .replace("{description}", tc["description"])
                .replace("{expectedResult}", tc["expectedResult"])
                .replace("{steps}", format_steps(tc["steps"]))
            )
            test_inputs.append(
                (f"TC-{i}", exec_prompt, args.test_depth, args.key, args.url))

    else:
        test_inputs.append(
            ("Single", args.execute, args.test_depth, args.key, args.url))

    # ------------------------------------------------------------------ #
    # 2 Run everything in parallel
    # ------------------------------------------------------------------ #
    start = time.time()
    tasks = [
        run_comprehensive_test(i, prompt, depth, key, url)
        for i, (name, prompt, depth, key, url) in enumerate(test_inputs)
    ]
    results = await asyncio.gather(*tasks)
    duration = round(time.time() - start, 2)

    if return_results:
        return results
    else:
        print(f"🏁 finished in {duration}s")
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
