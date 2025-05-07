from pathlib import Path
from dotenv import load_dotenv
import os, requests, json, asyncio, aiohttp, aiofiles, time

class AppConfig:
    def __init__(self):
        env_path = self._find_dotenv()
        load_dotenv(env_path)
        # data variables
        self.data_dir = self._get_project_root() / os.getenv('DATA_DIR', 'data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.data_dir / 'app.log'
        self.user_dir = self._get_project_root() / os.getenv('USER_DIR', 'user_posts')
        self.user_dir.mkdir(parents=True, exist_ok=True)
        # url web variables
        self.api_url = os.getenv('API_URL')
        self.timeout = int(os.getenv('TIMEOUT', '5'))
        self.users_url = os.getenv('USERS_ENDPOINT')
        self.posts_url = os.getenv('POSTS_ENDPOINT')
        if not self.api_url: raise ValueError('API_URL not set in .env')
        print('Initializing AppConfig Successfully')
        
    @staticmethod
    def _find_dotenv():
        current = Path(__file__).parent
        while current != current.parent:
            if (current / '.env').exists():
                return current / '.env'
            current = current.parent
        raise FileNotFoundError('.env not found in any parent directory')
    
    @staticmethod
    def _get_project_root():
        current = Path(__file__).parent
        while current != current.parent:
            if (current / "src").exists():
                return current
            current = current.parent
        raise FileNotFoundError("src directory not found in any parent directory")

class Data:
    def __init__(self, config: AppConfig):
        self.json_path = config.data_dir
        self.user_path = config.user_dir
        print("Initializing Data Successfully")
    
    async def save_data(self, data: list):
        tasks = []
        users, posts = data  # Unpack users and posts
        posts_by_user = {}
        if not users: raise ValueError('No users found')
        # Group posts by user ID
        for post in posts:
            user_id = post.get('userId', None)
            if user_id not in posts_by_user:
                posts_by_user[user_id] = []
            posts_by_user[user_id].append(post)

        # Create tasks for saving user data
        for user in users:
            user_posts = posts_by_user.get(user.get('id'), [])
            tasks.append(self._async_save_data([user, user_posts]))

        return await asyncio.gather(*tasks)

    
    async def _async_save_data(self, data: list):
        dir = self.user_path / str(data[0].get('id', None))
        dir.mkdir(parents=True, exist_ok=True)
        for id in data[1]:
            name = Path(dir) / ('post_' + str(id.get('id', None)) + '.json')
            async with aiofiles.open(name, mode='w') as file:
                await file.write(json.dumps(id))
    
class Organizer:
    def __init__(self, config: AppConfig, data: Data):
        self.api_url = config.api_url
        self.timeout = config.timeout
        self.data = data
        self.config = config
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
    
    async def _fetch_data(self, endpoint: str, params: dict = None):
        async with self.session.get(
                        self.api_url+endpoint,
                        params=params,
                        timeout=self.timeout
                        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def close(self):
        await self.session.close()

    async def fetch_all(self, user_id: int = None):
        data = await asyncio.gather(
            self._fetch_data(self.config.users_url, params={"id": user_id} if user_id else None),
            self._fetch_data(self.config.posts_url, params={"userId": user_id} if user_id else None)
        )
        return await self.data.save_data(data)

async def main():
    start = time.time()
    config = AppConfig()
    data = Data(config)
    worker = Organizer(config, data)
    try:
        await worker.fetch_all()
    finally:
        await worker.close()
    end = time.time()
    print(f'Took: {end-start:.2f}s')
    
if __name__ == "__main__":
    asyncio.run(main())