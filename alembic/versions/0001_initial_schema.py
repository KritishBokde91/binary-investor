"""initial schema for instruments, instrument_symbols, bars_1d, and analysis_results

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-08 19:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    # 1. instruments table
    op.create_table(
        'instruments',
        sa.Column('instrument_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('isin', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sector', sa.String(), nullable=False),
        sa.Column('listed_on', sa.Date(), nullable=True),
        sa.Column('delisted_on', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('instrument_id'),
        sa.UniqueConstraint('isin')
    )
    op.create_index(op.f('ix_instruments_isin'), 'instruments', ['isin'], unique=True)

    # 2. instrument_symbols table
    op.create_table(
        'instrument_symbols',
        sa.Column('instrument_id', sa.BigInteger(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['instrument_id'], ['instruments.instrument_id'], ),
        sa.PrimaryKeyConstraint('symbol', 'valid_from')
    )
    op.create_index('ix_instrument_symbols_lookup', 'instrument_symbols', ['symbol', 'valid_from', 'valid_to'], unique=False)

    # 3. bars_1d table
    op.create_table(
        'bars_1d',
        sa.Column('instrument_id', sa.BigInteger(), nullable=False),
        sa.Column('ts', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column('high', sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column('low', sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column('close', sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('deliv_qty', sa.BigInteger(), nullable=True),
        sa.Column('adj_factor', sa.Numeric(precision=18, scale=10), server_default='1.0', nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('ingested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('instrument_id', 'ts')
    )

    # 4. analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('instrument_id', sa.BigInteger(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('params_hash', sa.String(), nullable=False),
        sa.Column('data_version', sa.String(), nullable=False),
        sa.Column('model_version', sa.String(), nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('payload', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
        sa.PrimaryKeyConstraint('instrument_id', 'kind', 'params_hash', 'data_version')
    )
    op.create_index('ix_analysis_results_time_lookup', 'analysis_results', ['instrument_id', 'kind', sa.text('computed_at DESC')], unique=False)

    # TimescaleDB hypertable setup (conditional on PostgreSQL with TimescaleDB extension available)
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
        op.execute(sa.text("SELECT create_hypertable('bars_1d', 'ts', chunk_time_interval => INTERVAL '1 year', if_not_exists => TRUE);"))


def downgrade() -> None:
    op.drop_index('ix_analysis_results_time_lookup', table_name='analysis_results')
    op.drop_table('analysis_results')
    op.drop_table('bars_1d')
    op.drop_index('ix_instrument_symbols_lookup', table_name='instrument_symbols')
    op.drop_table('instrument_symbols')
    op.drop_index(op.f('ix_instruments_isin'), table_name='instruments')
    op.drop_table('instruments')
