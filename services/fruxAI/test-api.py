#!/usr/bin/env python3
"""
fruxAI API Test Script
Tests the fruxAI API endpoints and basic functionality.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any
import sys

class fruxAITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/fruxAI/api/v1"

    async def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        print("🔍 Testing health check...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health") as response:
                    result = await response.json()
                    if response.status == 200:
                        print("✅ Health check passed")
                        return {"status": "success", "data": result}
                    else:
                        print(f"❌ Health check failed: {response.status}")
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"status": "error", "error": str(e)}

    async def test_create_crawl_job(self) -> Dict[str, Any]:
        """Test creating a crawl job"""
        print("🔍 Testing crawl job creation...")
        try:
            job_data = {
                "job_id": f"test-job-{int(time.time())}",
                "url": "https://httpbin.org/html",
                "priority": 1,
                "crawl_type": "full",
                "max_depth": 1,
                "respect_robots": False,
                "rate_limit": 1.0
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/crawl-jobs",
                    json=job_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Crawl job created successfully")
                        return {"status": "success", "data": result, "job_id": job_data["job_id"]}
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create crawl job: {response.status} - {error_text}")
                        return {"status": "failed", "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            print(f"❌ Crawl job creation error: {e}")
            return {"status": "error", "error": str(e)}

    async def test_list_crawl_jobs(self) -> Dict[str, Any]:
        """Test listing crawl jobs"""
        print("🔍 Testing crawl jobs list...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/crawl-jobs") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Crawl jobs list retrieved ({len(result)} jobs)")
                        return {"status": "success", "data": result}
                    else:
                        print(f"❌ Failed to list crawl jobs: {response.status}")
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Crawl jobs list error: {e}")
            return {"status": "error", "error": str(e)}

    async def test_reports(self) -> Dict[str, Any]:
        """Test reports endpoint"""
        print("🔍 Testing reports...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/reports/crawl-stats") as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Reports retrieved successfully")
                        return {"status": "success", "data": result}
                    else:
                        print(f"❌ Failed to get reports: {response.status}")
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Reports error: {e}")
            return {"status": "error", "error": str(e)}

    async def test_metadata_creation(self, crawl_job_id: int) -> Dict[str, Any]:
        """Test creating metadata entry"""
        print("🔍 Testing metadata creation...")
        try:
            metadata_data = {
                "crawl_job_id": crawl_job_id,
                "url": "https://example.com/test",
                "title": "Test Page",
                "description": "A test page for fruxAI",
                "content_type": "text/html",
                "file_size": 1024,
                "crawl_depth": 0,
                "response_time": 0.5,
                "status_code": 200,
                "extracted_text": "This is a test page with some content.",
                "company_name": "Test Company",
                "company_email": "test@example.com",
                "company_website": "https://example.com"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/metadata",
                    json=metadata_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Metadata created successfully")
                        return {"status": "success", "data": result}
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create metadata: {response.status} - {error_text}")
                        return {"status": "failed", "error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            print(f"❌ Metadata creation error: {e}")
            return {"status": "error", "error": str(e)}

    async def test_company_reports(self) -> Dict[str, Any]:
        """Test company reports endpoint"""
        print("🔍 Testing company reports...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/companies") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Company reports retrieved ({len(result)} companies)")
                        return {"status": "success", "data": result}
                    else:
                        print(f"❌ Failed to get company reports: {response.status}")
                        return {"status": "failed", "error": f"HTTP {response.status}"}
        except Exception as e:
            print(f"❌ Company reports error: {e}")
            return {"status": "error", "error": str(e)}

    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting fruxAI API Tests")
        print("=" * 50)

        results = {}

        # Test 1: Health Check
        results["health"] = await self.test_health_check()

        # Test 2: Create Crawl Job
        job_result = await self.test_create_crawl_job()
        results["create_job"] = job_result

        # Test 3: List Crawl Jobs
        results["list_jobs"] = await self.test_list_crawl_jobs()

        # Test 4: Reports
        results["reports"] = await self.test_reports()

        # Test 5: Create Metadata (if we have a job)
        if job_result.get("status") == "success" and job_result.get("data"):
            crawl_job_id = job_result["data"]["id"]
            results["create_metadata"] = await self.test_metadata_creation(crawl_job_id)

        # Test 6: Company Reports
        results["company_reports"] = await self.test_company_reports()

        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary:")

        success_count = 0
        total_count = len(results)

        for test_name, result in results.items():
            status = result.get("status", "unknown")
            if status == "success":
                success_count += 1
                print(f"✅ {test_name}: {status}")
            else:
                print(f"❌ {test_name}: {status} - {result.get('error', 'Unknown error')}")

        print(f"\nOverall: {success_count}/{total_count} tests passed")

        if success_count == total_count:
            print("🎉 All tests passed! fruxAI API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the API configuration.")
            return False

async def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description="fruxAI API Test Script")
    parser.add_argument("--url", default="http://localhost:8001", help="fruxAI API base URL")
    parser.add_argument("--skip-wait", action="store_true", help="Skip waiting for API to be ready")

    args = parser.parse_args()

    if not args.skip_wait:
        print("⏳ Waiting for fruxAI API to be ready...")
        await asyncio.sleep(10)  # Give API time to start

    tester = fruxAITester(args.url)

    # Check if API is accessible
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{args.url}/fruxAI/api/v1/health", timeout=5) as response:
                if response.status != 200:
                    print(f"❌ fruxAI API is not accessible: HTTP {response.status}")
                    print("Make sure the API is running and accessible.")
                    sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to fruxAI API: {e}")
        print("Make sure the API is running and accessible.")
        sys.exit(1)

    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
