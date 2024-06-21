import yaml
import glob
import datetime
from mdutils.mdutils import MdUtils
from monthdelta import monthmod
from enum import Enum


class Language(Enum):
    C = "C"
    JAVA = "Java"
    KOTLIN = "Kotlin"


class Category(Enum):
    WEB = "Web"
    ANDROID = "Android"
    IOS = "iOS"


class Language:
    def __init__(
        self,
        language: str,
        framework: str,
        libraries: list[str],
    ):
        self.language = language
        self.framework = framework
        self.libraries = libraries

    def to_str(self) -> list[str, list[str]]:
        return [
            f'{self.language}{f" {self.framework}" if self.framework else ""}',
            self.libraries,
        ]


class Project:
    def __init__(
        self,
        key: str,
        title: str,
        categories: list[Category],
        descriptions: list[str],
        target: list[str],
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        team: list[dict],
        my_roles: list[str],
        backend_languages: list[Language],
        frontend_languages: list[Language],
        infrastructure: list[str],
        database: list[str],
        work: list[str],
    ):
        self.key = key
        self.title = title
        self.categories = categories
        self.descriptions = descriptions
        self.target = target
        self.start_date = start_date
        self.end_date = end_date
        self.team = team
        self.my_roles = my_roles
        self.backend_languages = backend_languages
        self.frontend_languages = frontend_languages
        self.infrastructure = infrastructure
        self.database = database
        self.work = work

    def get_term_month(self) -> tuple[int, int]:
        mmod = monthmod(self.start_date, self.end_date)
        return mmod[0].months // 12, mmod[0].months % 12

    def get_term(self) -> tuple[int, int]:
        y, m = self.get_term_month()
        return f'{"" if y == 0 else f"{y}年" }{"" if m == 0 else f"{m}か月" }'


origin_files = glob.glob(f"./origin/*")
origin_files.sort()

projects: list[Project] = []

for origin_file in origin_files:
    with open(origin_file, "r") as yml:
        project_yaml = yaml.safe_load(yml)
        projects.append(
            Project(
                origin_file.replace("./origin/", "").replace(".yaml", ""),
                project_yaml.get("title"),
                project_yaml.get("category"),
                project_yaml.get("description"),
                project_yaml.get("target"),
                project_yaml.get("start_date"),
                project_yaml.get("end_date"),
                ([] if not "team" in project_yaml else project_yaml["team"]),
                project_yaml.get("my_roles"),
                list(
                    map(
                        lambda l: Language(
                            l.get("language"),
                            l.get("framework"),
                            l.get("libraries", []),
                        ),
                        project_yaml["languages"].get("backend", []),
                    )
                ),
                list(
                    map(
                        lambda l: Language(
                            l.get("language"),
                            l.get("framework"),
                            l.get("libraries", []),
                        ),
                        project_yaml["languages"].get("frontend", []),
                    )
                ),
                project_yaml.get("infrastructure", []),
                project_yaml.get("database", []),
                project_yaml.get("work", []),
            )
        )

mdFileIndex = MdUtils(file_name="./projects/README.md", title="Projects")
for i, project in enumerate(projects):
    mdFileIndex.new_line(
        mdFileIndex.new_inline_link(link=f"./{project.key}.md", text=project.title)
    )
    mdFile = MdUtils(file_name=f"./projects/{project.key}.md", title=project.title)
    mdFile.new_header(level=1, title="工期")
    mdFile.new_line(project.get_term())
    mdFile.new_header(level=1, title="ユーザ")
    mdFile.new_line(", ".join(project.target))
    mdFile.new_header(level=1, title="概要")
    mdFile.new_list(project.descriptions)
    mdFile.new_header(level=1, title="チーム")
    mdFile.new_list(
        list(
            map(lambda member: f"{member['role']}: {member['number']}名", project.team)
        )
    )
    mdFile.new_header(level=2, title="自身の役割")
    mdFile.new_list(project.my_roles)
    mdFile.new_header(level=1, title="使用言語")
    mdFile.new_header(level=2, title="バックエンド")
    mdFile.new_list(
        list(
            filter(
                lambda x: len(x) > 0,
                sum(
                    list(map(lambda l: l.to_str(), project.backend_languages)),
                    [],
                ),
            ),
        )
    )
    mdFile.new_header(level=2, title="フロントエンド")
    mdFile.new_list(
        list(
            filter(
                lambda x: len(x) > 0,
                sum(
                    list(map(lambda l: l.to_str(), project.frontend_languages)),
                    [],
                ),
            ),
        )
    )
    mdFile.new_header(level=2, title="インフラ")
    mdFile.new_list(project.infrastructure)
    mdFile.new_header(level=2, title="DB")
    mdFile.new_list(project.database)
    mdFile.new_header(level=1, title="担当")
    mdFile.new_list(project.work)
    mdFile.create_md_file()
mdFileIndex.create_md_file()
