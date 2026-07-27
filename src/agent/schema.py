#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/7/23 18:19
# @Author  : name
# @File    : schema.py

from pydantic import BaseModel


class NetflixTitlesColumn(BaseModel):
    name: str
    type: str
    description: str  # 中文描述


class NetflixTitlesSchema(BaseModel):
    name: str
    description: str
    columns: list[NetflixTitlesColumn]
    sample_rows: int


# 数据库 schema 定义
DATABASE_SCHEMA = [
  NetflixTitlesSchema(
      name="netflix_titles",
      description="A tabular snapshot of titles available on Netflix, " \
                     "containing metadata for 8,807 titles (6,131 movies, 2,676 TV shows) as listed on the platform up to September 2021. " \
                     "Each row represents one title with cast, director, country of production, genre tags, " \
                     "content rating, runtime/season count, and a short synopsis.",
      columns=[
          NetflixTitlesColumn(
              name="show_id",
              type="varchar(1024)",
              description="唯一标识ID（主键）。例如 's1'。"
          ),
          NetflixTitlesColumn(
              name="type",
              type="varchar(1024)",
              description="内容类型：电影（Movie）或电视节目（TV Show）。"
          ),
          NetflixTitlesColumn(
              name="title",
              type="varchar(1024)",
              description="标题名称。"
          ),
          NetflixTitlesColumn(
              name="director",
              type="varchar(1024)",
              description="导演，多人时用逗号分隔（如 'Raúl Campos, Jan Suter'）。数据未归一化，无法区分单导演名字中的逗号和多导演。"
          ),
          NetflixTitlesColumn(
              name="cast",
              type="varchar(1024)",
              description="演员阵容，按出场顺序排列（用逗号分隔，但不保证顺序可靠）。"
          ),
          NetflixTitlesColumn(
              name="country",
              type="varchar(1024)",
              description="制作国家/地区，多国合作用逗号分隔。"
          ),
          NetflixTitlesColumn(
              name="date_added",
              type="varchar(1024)",
              description="添加到平台的日期，格式为 'Month DD, YYYY'（如 'January 1, 2020'）。时间范围：2008-01-01 至 2021-09-25。可用 pd.to_datetime 解析。"
          ),
          NetflixTitlesColumn(
              name="release_year",
              type="int",
              description="上映年份，范围 1925–2021。"
          ),
          NetflixTitlesColumn(
              name="rating",
              type="varchar(1024)",
              description="内容分级/评级（如 PG-13、TV-MA）。注意有3行数据存在异常值。"
          ),
          NetflixTitlesColumn(
              name="duration",
              type="varchar(1024)",
              description="时长：电影为 'X min'（分钟），电视节目为 'X Seasons'（季数）。需在解析前根据 type 字段区分单位。"
          ),
          NetflixTitlesColumn(
              name="listed_in",
              type="varchar(1024)",
              description="内容所属的分类/标签，多个标签用逗号分隔（如 'Dramas, International Movies'）。"
          ),
          NetflixTitlesColumn(
              name="description",
              type="varchar(1024)",
              description="内容的简短剧情描述。"
          )
      ],
      sample_rows=8807
  )
]

