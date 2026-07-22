from django.db import migrations

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    description VARCHAR(300) NOT NULL,
    image VARCHAR(64) NOT NULL DEFAULT 'http://127.0.0.1:9000/images/default.jpg',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS appeals (
    id BIGSERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES auth_user (id) ON DELETE CASCADE,
    helper_id INTEGER REFERENCES auth_user (id) ON DELETE CASCADE,
    status_id INTEGER NOT NULL,
    time_created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    time_applied TIMESTAMP WITH TIME ZONE,
    time_ended TIMESTAMP WITH TIME ZONE,
    connection_code VARCHAR(64) NOT NULL DEFAULT '',
    average_work_time INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS appeal_issues (
    id SERIAL PRIMARY KEY,
    appeal_id INTEGER NOT NULL REFERENCES appeals (id) ON DELETE CASCADE,
    issue_id INTEGER NOT NULL REFERENCES issues (id) ON DELETE CASCADE,
    count INTEGER NOT NULL CHECK (count >= 1),
    UNIQUE (appeal_id, issue_id)
);
"""

DROP_SQL = """
DROP TABLE IF EXISTS appeal_issues;
DROP TABLE IF EXISTS appeals;
DROP TABLE IF EXISTS issues;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("remote_support", "0001_initial"),
        ("auth", "__latest__"),
    ]

    operations = [
        migrations.RunSQL(CREATE_SQL, reverse_sql=DROP_SQL),
    ]
