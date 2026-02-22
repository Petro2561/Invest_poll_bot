from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Database:
    url: str


@dataclass
class Redis:
    host: str
    port: int
    db: int
    data: str


@dataclass
class ExpertChannel:
    channel_username: str  # @username канала эксперта


@dataclass
class AdminConfig:
    admin_login: str
    admin_password: str
    secret_key: str


@dataclass
class Scheduler:
    url: str
    timezone: str


@dataclass
class WebhookConfig:
    use: bool
    base_url: str
    path: str
    port: int
    host: str

    def build_url(self) -> str:
        return f"{self.base_url}{self.path}"


@dataclass
class Config:
    tg_bot: TgBot
    database: Database
    redis: Redis
    admin_config: AdminConfig
    scheduler: Scheduler
    expert_channel: ExpertChannel



def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN")),
        database=Database(url=env("DATABASE_URL")),
        redis=Redis(
            host=env("REDIS_HOST"),
            port=env("REDIS_PORT"),
            db=env("REDIS_DB"),
            data=env("REDIS_DATA"),
        ),
        admin_config=AdminConfig(
            admin_login=env("ADMIN_LOGIN"),
            admin_password=env("ADMIN_PASSWORD"),
            secret_key=env("SECRET_KEY"),
        ),
        scheduler=Scheduler(url=env("SCHEDULER_URL"), timezone=env("TIMEZONE")),
        expert_channel=ExpertChannel(channel_username=env("EXPERT_CHANNEL_USERNAME", default="@expert_channel"))
    )
