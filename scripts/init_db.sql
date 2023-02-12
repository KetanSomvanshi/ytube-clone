
-- init script to initialize the database table
CREATE TABLE public.ytubemeta (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	external_id varchar(255) NULL,
	title text NOT NULL,
	description varchar NOT NULL,
	published_at timestamptz NULL,
	channel_id varchar(255) NULL,
	channel_title text NULL,
	thumbnails json NULL,
--	search_data is precomputed ts_vector column for full text search , computed using title and description fields
	search_data tsvector NULL GENERATED ALWAYS AS (to_tsvector('english'::regconfig, (title || ' '::text) || description::text)) STORED,
	CONSTRAINT ytubemeta_pk PRIMARY KEY (id),
	CONSTRAINT ytubemeta_un UNIQUE (external_id)
);
-- create gin index on search_data column for faster search queries
CREATE INDEX search_data_gin_idx ON public.ytubemeta USING gin (search_data);