"""Refactor Historical

迁移 ID: 3c25a5a8c050
父迁移: b7fbdafc339a
创建时间: 2024-05-14 09:16:35.193001

"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from alembic import op
from nonebot.log import logger
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn
from sqlalchemy import desc, select
from sqlalchemy.dialects import sqlite
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = '3c25a5a8c050'
down_revision: str | Sequence[str] | None = 'b7fbdafc339a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def migrate_old_data() -> None:
    from json import dumps, loads

    Base = automap_base()  # noqa: N806
    Base.prepare(autoload_with=op.get_bind())
    OldHistoricalData = Base.classes.nonebot_plugin_tetris_stats_historicaldata  # noqa: N806
    TETRIOHistoricalData = Base.classes.nonebot_plugin_tetris_stats_tetriohistoricaldata  # noqa: N806
    TOSHistoricalData = Base.classes.nonebot_plugin_tetris_stats_toshistoricaldata  # noqa: N806
    with (
        Session(op.get_bind()) as session,
        Progress(
            TextColumn('[progress.description]{task.description}'),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        ) as progress,
    ):
        if session.query(OldHistoricalData).count() == 0:
            logger.info('空表, 跳过')
            return
        task_id = progress.add_task('[cyan]Migrating:', total=session.query(OldHistoricalData).count())
        pointer = 0
        while pointer < session.query(OldHistoricalData).order_by(desc(OldHistoricalData.id)).limit(1).one().id:
            result = session.scalars(
                select(OldHistoricalData)
                .where(OldHistoricalData.id > pointer)
                .order_by(OldHistoricalData.id)
                .limit(100)
            ).all()
            for j in result:
                processed_data: dict[str, Any] = loads(j.processed_data)
                if j.game_platform == 'IO':
                    if (data := processed_data.get('user_info')) is not None:
                        session.add(
                            TETRIOHistoricalData(
                                user_unique_identifier=j.user_unique_identifier,
                                api_type='User Info',
                                data=dumps(data),
                                update_time=datetime.fromisoformat(data['cache']['cached_at']),
                            )
                        )
                    if (data := processed_data.get('user_records')) is not None:
                        session.add(
                            TETRIOHistoricalData(
                                user_unique_identifier=j.user_unique_identifier,
                                api_type='User Records',
                                data=dumps(data),
                                update_time=datetime.fromisoformat(data['cache']['cached_at']),
                            )
                        )
                if j.game_platform == 'TOS' and not j.user_unique_identifier.isdigit():
                    if (data := processed_data.get('user_info')) is not None:
                        session.add(
                            TOSHistoricalData(
                                user_unique_identifier=j.user_unique_identifier,
                                api_type='User Info',
                                data=dumps(data),
                                update_time=j.finish_time,
                            )
                        )
                    if (data := processed_data.get('user_profile')) is not None:
                        for v in data.values():
                            session.add(
                                TOSHistoricalData(
                                    user_unique_identifier=j.user_unique_identifier,
                                    api_type='User Profile',
                                    data=dumps(v),
                                    update_time=j.finish_time,
                                )
                            )
                progress.update(task_id, advance=1)
            session.commit()
            pointer = result[-1].id
    logger.success('Migrate successfully')


def upgrade(name: str = '') -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'nonebot_plugin_tetris_stats_tetriohistoricaldata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_unique_identifier', sa.String(length=24), nullable=False),
        sa.Column('api_type', sa.String(length=16), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_nonebot_plugin_tetris_stats_tetriohistoricaldata')),
        info={'bind_key': 'nonebot_plugin_tetris_stats'},
    )
    with op.batch_alter_table('nonebot_plugin_tetris_stats_tetriohistoricaldata', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_api_type'), ['api_type'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_update_time'), ['update_time'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_user_unique_identifier'),
            ['user_unique_identifier'],
            unique=False,
        )

    op.create_table(
        'nonebot_plugin_tetris_stats_tophistoricaldata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_unique_identifier', sa.String(length=24), nullable=False),
        sa.Column('api_type', sa.String(length=16), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_nonebot_plugin_tetris_stats_tophistoricaldata')),
        info={'bind_key': 'nonebot_plugin_tetris_stats'},
    )
    with op.batch_alter_table('nonebot_plugin_tetris_stats_tophistoricaldata', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_api_type'), ['api_type'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_update_time'), ['update_time'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_user_unique_identifier'),
            ['user_unique_identifier'],
            unique=False,
        )

    op.create_table(
        'nonebot_plugin_tetris_stats_toshistoricaldata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_unique_identifier', sa.String(length=24), nullable=False),
        sa.Column('api_type', sa.String(length=16), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_nonebot_plugin_tetris_stats_toshistoricaldata')),
        info={'bind_key': 'nonebot_plugin_tetris_stats'},
    )
    with op.batch_alter_table('nonebot_plugin_tetris_stats_toshistoricaldata', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_api_type'), ['api_type'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_update_time'), ['update_time'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_user_unique_identifier'),
            ['user_unique_identifier'],
            unique=False,
        )

    op.create_table(
        'nonebot_plugin_tetris_stats_triggerhistoricaldata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trigger_time', sa.DateTime(), nullable=False),
        sa.Column('session_persist_id', sa.Integer(), nullable=False),
        sa.Column('game_platform', sa.String(length=32), nullable=False),
        sa.Column('command_type', sa.String(length=16), nullable=False),
        sa.Column('command_args', sa.JSON(), nullable=False),
        sa.Column('finish_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_nonebot_plugin_tetris_stats_triggerhistoricaldata')),
        info={'bind_key': 'nonebot_plugin_tetris_stats'},
    )
    with op.batch_alter_table('nonebot_plugin_tetris_stats_triggerhistoricaldata', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_triggerhistoricaldata_command_type'),
            ['command_type'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_nonebot_plugin_tetris_stats_triggerhistoricaldata_game_platform'),
            ['game_platform'],
            unique=False,
        )

    migrate_old_data()

    with op.batch_alter_table('nonebot_plugin_tetris_stats_historicaldata', schema=None) as batch_op:
        batch_op.drop_index('ix_nonebot_plugin_tetris_stats_historicaldata_command_type')
        batch_op.drop_index('ix_nonebot_plugin_tetris_stats_historicaldata_game_platform')
        batch_op.drop_index('ix_nonebot_plugin_tetris_stats_historicaldata_source_account')
        batch_op.drop_index('ix_nonebot_plugin_tetris_stats_historicaldata_source_type')
        batch_op.drop_index('ix_nonebot_plugin_tetris_stats_historicaldata_user_unique_identifier')

    op.drop_table('nonebot_plugin_tetris_stats_historicaldata')
    # ### end Alembic commands ###


def downgrade(name: str = '') -> None:
    if name:
        return
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'nonebot_plugin_tetris_stats_historicaldata',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('trigger_time', sa.DATETIME(), nullable=False),
        sa.Column('bot_platform', sa.VARCHAR(length=32), nullable=True),
        sa.Column('bot_account', sa.VARCHAR(), nullable=True),
        sa.Column('source_type', sa.VARCHAR(length=32), nullable=True),
        sa.Column('source_account', sa.VARCHAR(), nullable=True),
        sa.Column('message', sa.BLOB(), nullable=True),
        sa.Column('game_platform', sa.VARCHAR(length=32), nullable=False),
        sa.Column('command_type', sa.VARCHAR(length=16), nullable=False),
        sa.Column('command_args', sqlite.JSON(), nullable=False),
        sa.Column('game_user', sqlite.JSON(), nullable=False),
        sa.Column('processed_data', sqlite.JSON(), nullable=False),
        sa.Column('finish_time', sa.DATETIME(), nullable=False),
        sa.Column('user_unique_identifier', sa.VARCHAR(length=32), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_nonebot_plugin_tetris_stats_historicaldata'),
    )
    with op.batch_alter_table('nonebot_plugin_tetris_stats_historicaldata', schema=None) as batch_op:
        batch_op.create_index(
            'ix_nonebot_plugin_tetris_stats_historicaldata_user_unique_identifier',
            ['user_unique_identifier'],
            unique=False,
        )
        batch_op.create_index(
            'ix_nonebot_plugin_tetris_stats_historicaldata_source_type', ['source_type'], unique=False
        )
        batch_op.create_index(
            'ix_nonebot_plugin_tetris_stats_historicaldata_source_account', ['source_account'], unique=False
        )
        batch_op.create_index(
            'ix_nonebot_plugin_tetris_stats_historicaldata_game_platform', ['game_platform'], unique=False
        )
        batch_op.create_index(
            'ix_nonebot_plugin_tetris_stats_historicaldata_command_type', ['command_type'], unique=False
        )

    with op.batch_alter_table('nonebot_plugin_tetris_stats_triggerhistoricaldata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_triggerhistoricaldata_game_platform'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_triggerhistoricaldata_command_type'))

    op.drop_table('nonebot_plugin_tetris_stats_triggerhistoricaldata')
    with op.batch_alter_table('nonebot_plugin_tetris_stats_toshistoricaldata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_user_unique_identifier'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_update_time'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_toshistoricaldata_api_type'))

    op.drop_table('nonebot_plugin_tetris_stats_toshistoricaldata')
    with op.batch_alter_table('nonebot_plugin_tetris_stats_tophistoricaldata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_user_unique_identifier'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_update_time'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tophistoricaldata_api_type'))

    op.drop_table('nonebot_plugin_tetris_stats_tophistoricaldata')
    with op.batch_alter_table('nonebot_plugin_tetris_stats_tetriohistoricaldata', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_user_unique_identifier'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_update_time'))
        batch_op.drop_index(batch_op.f('ix_nonebot_plugin_tetris_stats_tetriohistoricaldata_api_type'))

    op.drop_table('nonebot_plugin_tetris_stats_tetriohistoricaldata')
    # ### end Alembic commands ###
