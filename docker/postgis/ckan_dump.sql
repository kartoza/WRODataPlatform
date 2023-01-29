--
-- PostgreSQL database dump
--

-- Dumped from database version 12.11 (Ubuntu 12.11-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.11 (Ubuntu 12.11-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: log_level; Type: TYPE; Schema: public; Owner: ckan_default
--

CREATE TYPE public.log_level AS ENUM (
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL'
);


ALTER TYPE public.log_level OWNER TO ckan_default;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.activity (
    id text NOT NULL,
    "timestamp" timestamp without time zone,
    user_id text,
    object_id text,
    revision_id text,
    activity_type text,
    data text
);


ALTER TABLE public.activity OWNER TO ckan_default;

--
-- Name: activity_detail; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.activity_detail (
    id text NOT NULL,
    activity_id text,
    object_id text,
    object_type text,
    activity_type text,
    data text
);


ALTER TABLE public.activity_detail OWNER TO ckan_default;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ckan_default;

--
-- Name: api_token; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.api_token (
    id text NOT NULL,
    name text,
    user_id text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_access timestamp without time zone,
    plugin_extras jsonb
);


ALTER TABLE public.api_token OWNER TO ckan_default;

--
-- Name: dashboard; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.dashboard (
    user_id text NOT NULL,
    activity_stream_last_viewed timestamp without time zone NOT NULL,
    email_last_sent timestamp without time zone DEFAULT LOCALTIMESTAMP NOT NULL
);


ALTER TABLE public.dashboard OWNER TO ckan_default;

--
-- Name: group; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public."group" (
    id text NOT NULL,
    name text NOT NULL,
    title text,
    description text,
    created timestamp without time zone,
    state text,
    type text NOT NULL,
    approval_status text,
    image_url text,
    is_organization boolean DEFAULT false
);


ALTER TABLE public."group" OWNER TO ckan_default;

--
-- Name: group_extra; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.group_extra (
    id text NOT NULL,
    group_id text,
    key text,
    value text,
    state text
);


ALTER TABLE public.group_extra OWNER TO ckan_default;

--
-- Name: group_extra_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.group_extra_revision (
    id text NOT NULL,
    group_id text,
    key text,
    value text,
    state text,
    revision_id text NOT NULL,
    continuity_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean
);


ALTER TABLE public.group_extra_revision OWNER TO ckan_default;

--
-- Name: group_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.group_revision (
    id text NOT NULL,
    name text NOT NULL,
    title text,
    description text,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    state text,
    revision_id text NOT NULL,
    continuity_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean,
    type text NOT NULL,
    approval_status text,
    image_url text,
    is_organization boolean DEFAULT false
);


ALTER TABLE public.group_revision OWNER TO ckan_default;

--
-- Name: harvest_gather_error; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_gather_error (
    id text NOT NULL,
    harvest_job_id text,
    message text,
    created timestamp without time zone
);


ALTER TABLE public.harvest_gather_error OWNER TO ckan_default;

--
-- Name: harvest_job; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_job (
    id text NOT NULL,
    created timestamp without time zone,
    gather_started timestamp without time zone,
    gather_finished timestamp without time zone,
    finished timestamp without time zone,
    source_id text,
    status text NOT NULL
);


ALTER TABLE public.harvest_job OWNER TO ckan_default;

--
-- Name: harvest_log; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_log (
    id text NOT NULL,
    content text NOT NULL,
    level public.log_level,
    created timestamp without time zone
);


ALTER TABLE public.harvest_log OWNER TO ckan_default;

--
-- Name: harvest_object; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_object (
    id text NOT NULL,
    guid text,
    current boolean,
    gathered timestamp without time zone,
    fetch_started timestamp without time zone,
    content text,
    fetch_finished timestamp without time zone,
    import_started timestamp without time zone,
    import_finished timestamp without time zone,
    state text,
    metadata_modified_date timestamp without time zone,
    retry_times integer,
    harvest_job_id text,
    harvest_source_id text,
    package_id text,
    report_status text
);


ALTER TABLE public.harvest_object OWNER TO ckan_default;

--
-- Name: harvest_object_error; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_object_error (
    id text NOT NULL,
    harvest_object_id text,
    message text,
    stage text,
    line integer,
    created timestamp without time zone
);


ALTER TABLE public.harvest_object_error OWNER TO ckan_default;

--
-- Name: harvest_object_extra; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_object_extra (
    id text NOT NULL,
    harvest_object_id text,
    key text,
    value text
);


ALTER TABLE public.harvest_object_extra OWNER TO ckan_default;

--
-- Name: harvest_source; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.harvest_source (
    id text NOT NULL,
    url text NOT NULL,
    title text,
    description text,
    config text,
    created timestamp without time zone,
    type text NOT NULL,
    active boolean,
    user_id text,
    publisher_id text,
    frequency text,
    next_run timestamp without time zone
);


ALTER TABLE public.harvest_source OWNER TO ckan_default;

--
-- Name: member; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.member (
    id text NOT NULL,
    group_id text,
    table_id text NOT NULL,
    state text,
    table_name text NOT NULL,
    capacity text NOT NULL
);


ALTER TABLE public.member OWNER TO ckan_default;

--
-- Name: member_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.member_revision (
    id text NOT NULL,
    table_id text NOT NULL,
    group_id text,
    state text,
    revision_id text NOT NULL,
    continuity_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean,
    table_name text NOT NULL,
    capacity text NOT NULL
);


ALTER TABLE public.member_revision OWNER TO ckan_default;

--
-- Name: package; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package (
    id text NOT NULL,
    name character varying(100) NOT NULL,
    title text,
    version character varying(100),
    url text,
    notes text,
    author text,
    author_email text,
    maintainer text,
    maintainer_email text,
    state text,
    license_id text,
    type text,
    owner_org text,
    private boolean DEFAULT false,
    metadata_modified timestamp without time zone,
    creator_user_id text,
    metadata_created timestamp without time zone
);


ALTER TABLE public.package OWNER TO ckan_default;

--
-- Name: package_extent; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_extent (
    package_id text NOT NULL,
    the_geom public.geometry(Geometry,4326)
);


ALTER TABLE public.package_extent OWNER TO ckan_default;

--
-- Name: package_extra; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_extra (
    id text NOT NULL,
    key text,
    value text,
    state text,
    package_id text
);


ALTER TABLE public.package_extra OWNER TO ckan_default;

--
-- Name: package_extra_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_extra_revision (
    id text NOT NULL,
    key text,
    value text,
    revision_id text NOT NULL,
    state text,
    package_id text,
    continuity_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean
);


ALTER TABLE public.package_extra_revision OWNER TO ckan_default;

--
-- Name: package_member; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_member (
    package_id text NOT NULL,
    user_id text NOT NULL,
    capacity text NOT NULL,
    modified timestamp without time zone NOT NULL
);


ALTER TABLE public.package_member OWNER TO ckan_default;

--
-- Name: package_relationship; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_relationship (
    id text NOT NULL,
    subject_package_id text,
    object_package_id text,
    type text,
    comment text,
    state text
);


ALTER TABLE public.package_relationship OWNER TO ckan_default;

--
-- Name: package_relationship_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_relationship_revision (
    id text NOT NULL,
    subject_package_id text,
    object_package_id text,
    type text,
    comment text,
    revision_id text NOT NULL,
    continuity_id text,
    state text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean
);


ALTER TABLE public.package_relationship_revision OWNER TO ckan_default;

--
-- Name: package_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_revision (
    id text NOT NULL,
    name character varying(100) NOT NULL,
    title text,
    version character varying(100),
    url text,
    notes text,
    author text,
    author_email text,
    maintainer text,
    maintainer_email text,
    revision_id text NOT NULL,
    state text,
    continuity_id text,
    license_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean,
    type text,
    owner_org text,
    private boolean DEFAULT false,
    metadata_modified timestamp without time zone,
    creator_user_id text,
    metadata_created timestamp without time zone
);


ALTER TABLE public.package_revision OWNER TO ckan_default;

--
-- Name: package_tag; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_tag (
    id text NOT NULL,
    state text,
    package_id text,
    tag_id text
);


ALTER TABLE public.package_tag OWNER TO ckan_default;

--
-- Name: package_tag_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.package_tag_revision (
    id text NOT NULL,
    revision_id text NOT NULL,
    state text,
    package_id text,
    tag_id text,
    continuity_id text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean
);


ALTER TABLE public.package_tag_revision OWNER TO ckan_default;

--
-- Name: rating; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.rating (
    id text NOT NULL,
    user_id text,
    user_ip_address text,
    rating double precision,
    created timestamp without time zone,
    package_id text
);


ALTER TABLE public.rating OWNER TO ckan_default;

--
-- Name: resource; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.resource (
    id text NOT NULL,
    url text NOT NULL,
    format text,
    description text,
    "position" integer,
    hash text,
    state text,
    extras text,
    name text,
    resource_type text,
    mimetype text,
    mimetype_inner text,
    size bigint,
    last_modified timestamp without time zone,
    cache_url text,
    cache_last_updated timestamp without time zone,
    webstore_url text,
    webstore_last_updated timestamp without time zone,
    created timestamp without time zone,
    url_type text,
    package_id text DEFAULT ''::text NOT NULL,
    metadata_modified timestamp without time zone
);


ALTER TABLE public.resource OWNER TO ckan_default;

--
-- Name: resource_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.resource_revision (
    id text NOT NULL,
    url text NOT NULL,
    format text,
    description text,
    "position" integer,
    revision_id text NOT NULL,
    hash text,
    state text,
    continuity_id text,
    extras text,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean,
    name text,
    resource_type text,
    mimetype text,
    mimetype_inner text,
    size bigint,
    last_modified timestamp without time zone,
    cache_url text,
    cache_last_updated timestamp without time zone,
    webstore_url text,
    webstore_last_updated timestamp without time zone,
    created timestamp without time zone,
    url_type text,
    package_id text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.resource_revision OWNER TO ckan_default;

--
-- Name: resource_view; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.resource_view (
    id text NOT NULL,
    resource_id text,
    title text,
    description text,
    view_type text NOT NULL,
    "order" integer NOT NULL,
    config text
);


ALTER TABLE public.resource_view OWNER TO ckan_default;

--
-- Name: revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.revision (
    id text NOT NULL,
    "timestamp" timestamp without time zone,
    author character varying(200),
    message text,
    state text,
    approved_timestamp timestamp without time zone
);


ALTER TABLE public.revision OWNER TO ckan_default;

--
-- Name: system_info; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.system_info (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value text,
    state text DEFAULT 'active'::text NOT NULL
);


ALTER TABLE public.system_info OWNER TO ckan_default;

--
-- Name: system_info_id_seq; Type: SEQUENCE; Schema: public; Owner: ckan_default
--

CREATE SEQUENCE public.system_info_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_info_id_seq OWNER TO ckan_default;

--
-- Name: system_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ckan_default
--

ALTER SEQUENCE public.system_info_id_seq OWNED BY public.system_info.id;


--
-- Name: system_info_revision; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.system_info_revision (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value text,
    revision_id text NOT NULL,
    continuity_id integer,
    state text DEFAULT 'active'::text NOT NULL,
    expired_id text,
    revision_timestamp timestamp without time zone,
    expired_timestamp timestamp without time zone,
    current boolean
);


ALTER TABLE public.system_info_revision OWNER TO ckan_default;

--
-- Name: tag; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.tag (
    id text NOT NULL,
    name character varying(100) NOT NULL,
    vocabulary_id character varying(100)
);


ALTER TABLE public.tag OWNER TO ckan_default;

--
-- Name: task_status; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.task_status (
    id text NOT NULL,
    entity_id text NOT NULL,
    entity_type text NOT NULL,
    task_type text NOT NULL,
    key text NOT NULL,
    value text NOT NULL,
    state text,
    error text,
    last_updated timestamp without time zone
);


ALTER TABLE public.task_status OWNER TO ckan_default;

--
-- Name: term_translation; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.term_translation (
    term text NOT NULL,
    term_translation text NOT NULL,
    lang_code text NOT NULL
);


ALTER TABLE public.term_translation OWNER TO ckan_default;

--
-- Name: tracking_raw; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.tracking_raw (
    user_key character varying(100) NOT NULL,
    url text NOT NULL,
    tracking_type character varying(10) NOT NULL,
    access_timestamp timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.tracking_raw OWNER TO ckan_default;

--
-- Name: tracking_summary; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.tracking_summary (
    url text NOT NULL,
    package_id text,
    tracking_type character varying(10) NOT NULL,
    count integer NOT NULL,
    running_total integer DEFAULT 0 NOT NULL,
    recent_views integer DEFAULT 0 NOT NULL,
    tracking_date date
);


ALTER TABLE public.tracking_summary OWNER TO ckan_default;

--
-- Name: user; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public."user" (
    id text NOT NULL,
    name text NOT NULL,
    apikey text,
    created timestamp without time zone,
    about text,
    password text,
    fullname text,
    email text,
    reset_key text,
    sysadmin boolean DEFAULT false,
    activity_streams_email_notifications boolean DEFAULT false,
    state text DEFAULT 'active'::text NOT NULL,
    plugin_extras jsonb,
    image_url text
);


ALTER TABLE public."user" OWNER TO ckan_default;

--
-- Name: user_following_dataset; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.user_following_dataset (
    follower_id text NOT NULL,
    object_id text NOT NULL,
    datetime timestamp without time zone NOT NULL
);


ALTER TABLE public.user_following_dataset OWNER TO ckan_default;

--
-- Name: user_following_group; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.user_following_group (
    follower_id text NOT NULL,
    object_id text NOT NULL,
    datetime timestamp without time zone NOT NULL
);


ALTER TABLE public.user_following_group OWNER TO ckan_default;

--
-- Name: user_following_user; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.user_following_user (
    follower_id text NOT NULL,
    object_id text NOT NULL,
    datetime timestamp without time zone NOT NULL
);


ALTER TABLE public.user_following_user OWNER TO ckan_default;

--
-- Name: vocabulary; Type: TABLE; Schema: public; Owner: ckan_default
--

CREATE TABLE public.vocabulary (
    id text NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.vocabulary OWNER TO ckan_default;

--
-- Name: system_info id; Type: DEFAULT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info ALTER COLUMN id SET DEFAULT nextval('public.system_info_id_seq'::regclass);


--
-- Data for Name: activity; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.activity (id, "timestamp", user_id, object_id, revision_id, activity_type, data) FROM stdin;
ece64f92-0e2c-4a8a-905a-f31b918e8d14	2022-06-19 23:26:02.134798	3b76adea-3193-4483-8bde-ee8770366329	3b76adea-3193-4483-8bde-ee8770366329	\N	new user	\N
56dd534d-2bb7-4d4b-84ce-2ee2009d151b	2022-06-19 23:26:40.417446	3b76adea-3193-4483-8bde-ee8770366329	29158435-90fb-482f-b30a-aaf733338698	\N	new organization	{"group": {"id": "29158435-90fb-482f-b30a-aaf733338698", "name": "kartoza", "title": "kartoza", "type": "organization", "description": "where the fun is", "image_url": "https://avatars.githubusercontent.com/u/7395888?s=200&v=4", "created": "2022-06-20T01:26:40.412505", "is_organization": true, "approval_status": "approved", "state": "active"}}
\.


--
-- Data for Name: activity_detail; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.activity_detail (id, activity_id, object_id, object_type, activity_type, data) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.alembic_version (version_num) FROM stdin;
ccd38ad5fced
\.


--
-- Data for Name: api_token; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.api_token (id, name, user_id, created_at, last_access, plugin_extras) FROM stdin;
\.


--
-- Data for Name: dashboard; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.dashboard (user_id, activity_stream_last_viewed, email_last_sent) FROM stdin;
3b76adea-3193-4483-8bde-ee8770366329	2022-06-19 23:26:02.143206	2022-06-19 23:26:02.143211
\.


--
-- Data for Name: group; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public."group" (id, name, title, description, created, state, type, approval_status, image_url, is_organization) FROM stdin;
29158435-90fb-482f-b30a-aaf733338698	kartoza	kartoza	where the fun is	2022-06-20 01:26:40.412505	active	organization	approved	https://avatars.githubusercontent.com/u/7395888?s=200&v=4	t
\.


--
-- Data for Name: group_extra; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.group_extra (id, group_id, key, value, state) FROM stdin;
\.


--
-- Data for Name: group_extra_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.group_extra_revision (id, group_id, key, value, state, revision_id, continuity_id, expired_id, revision_timestamp, expired_timestamp, current) FROM stdin;
\.


--
-- Data for Name: group_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.group_revision (id, name, title, description, created, state, revision_id, continuity_id, expired_id, revision_timestamp, expired_timestamp, current, type, approval_status, image_url, is_organization) FROM stdin;
\.


--
-- Data for Name: harvest_gather_error; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_gather_error (id, harvest_job_id, message, created) FROM stdin;
\.


--
-- Data for Name: harvest_job; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_job (id, created, gather_started, gather_finished, finished, source_id, status) FROM stdin;
\.


--
-- Data for Name: harvest_log; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_log (id, content, level, created) FROM stdin;
\.


--
-- Data for Name: harvest_object; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_object (id, guid, current, gathered, fetch_started, content, fetch_finished, import_started, import_finished, state, metadata_modified_date, retry_times, harvest_job_id, harvest_source_id, package_id, report_status) FROM stdin;
\.


--
-- Data for Name: harvest_object_error; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_object_error (id, harvest_object_id, message, stage, line, created) FROM stdin;
\.


--
-- Data for Name: harvest_object_extra; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_object_extra (id, harvest_object_id, key, value) FROM stdin;
\.


--
-- Data for Name: harvest_source; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.harvest_source (id, url, title, description, config, created, type, active, user_id, publisher_id, frequency, next_run) FROM stdin;
\.


--
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.member (id, group_id, table_id, state, table_name, capacity) FROM stdin;
26006957-b836-441b-8127-54aa60002a54	29158435-90fb-482f-b30a-aaf733338698	3b76adea-3193-4483-8bde-ee8770366329	active	user	admin
25889ba9-3458-458c-8867-bf9ab00f58c5	29158435-90fb-482f-b30a-aaf733338698	d0293dda-bffb-4cc0-a8c0-2a486d3828fa	active	package	organization
65644959-f9e6-47a2-881f-9a88612bbcfa	29158435-90fb-482f-b30a-aaf733338698	85571fc5-9482-460e-89a6-164bfd936317	active	package	organization
\.


--
-- Data for Name: member_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.member_revision (id, table_id, group_id, state, revision_id, continuity_id, expired_id, revision_timestamp, expired_timestamp, current, table_name, capacity) FROM stdin;
\.


--
-- Data for Name: package; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package (id, name, title, version, url, notes, author, author_email, maintainer, maintainer_email, state, license_id, type, owner_org, private, metadata_modified, creator_user_id, metadata_created) FROM stdin;
d0293dda-bffb-4cc0-a8c0-2a486d3828fa	t1	t1	\N	\N	\N	\N	\N	\N	\N	draft	\N	metadata-form	29158435-90fb-482f-b30a-aaf733338698	t	2022-06-20 02:23:04.011049	3b76adea-3193-4483-8bde-ee8770366329	2022-06-20 02:10:32.419379
85571fc5-9482-460e-89a6-164bfd936317	dataset1	dataset1	\N	\N	\N	\N	\N	\N	\N	draft	\N	metadata-form	29158435-90fb-482f-b30a-aaf733338698	t	2022-06-21 07:25:32.465033	3b76adea-3193-4483-8bde-ee8770366329	2022-06-21 07:25:32.465027
\.


--
-- Data for Name: package_extent; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_extent (package_id, the_geom) FROM stdin;
d0293dda-bffb-4cc0-a8c0-2a486d3828fa	0103000020E61000000100000005000000F163CC5D4B783040AAF1D24D622036C05F07CE1951724040AAF1D24D622036C05F07CE1951724040D3BCE3141D6941C0F163CC5D4B783040D3BCE3141D6941C0F163CC5D4B783040AAF1D24D622036C0
85571fc5-9482-460e-89a6-164bfd936317	0103000020E61000000100000005000000F163CC5D4B783040AAF1D24D622036C05F07CE1951724040AAF1D24D622036C05F07CE1951724040D3BCE3141D6941C0F163CC5D4B783040D3BCE3141D6941C0F163CC5D4B783040AAF1D24D622036C0
\.


--
-- Data for Name: package_extra; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_extra (id, key, value, state, package_id) FROM stdin;
31f93cdc-0f2c-46d2-b0b0-8f7d8d84b67d	data_collection_organization		active	85571fc5-9482-460e-89a6-164bfd936317
13712287-2f67-431f-b46b-4d40eaf654f7	data_reference_date	[{"data_reference_date_from": null, "data_reference_date_to": null}]	active	85571fc5-9482-460e-89a6-164bfd936317
96783859-cbef-431e-b954-536cebb3a591	keywords	metadata	active	85571fc5-9482-460e-89a6-164bfd936317
97389b46-3d3e-426b-a62f-8d8747337d8c	license	Open (Creative Commons)	active	85571fc5-9482-460e-89a6-164bfd936317
a819ad36-8e33-45e1-bad2-8846e527e5eb	dataset_language		active	85571fc5-9482-460e-89a6-164bfd936317
eb8aeed7-7b43-4457-88fe-d752d3e00eb5	data_classification	static	active	85571fc5-9482-460e-89a6-164bfd936317
11a11ed1-af45-484c-aa4d-3e69d4b7bcc8	uploader_estimation_of_extent	raw	active	85571fc5-9482-460e-89a6-164bfd936317
23c598c8-058b-4208-8dc8-e5be94067858	minimum_maximum_extent	[{"maximum_vertical_extent": "", "minimum_vertical_extent": ""}]	active	85571fc5-9482-460e-89a6-164bfd936317
1b80876c-1612-452a-88f4-cfe8848561c4	alternative_identifier		active	85571fc5-9482-460e-89a6-164bfd936317
8a99d61b-f93c-4e56-bc32-a04ff53bf9aa	contact_person	[{"contact_department": "", "contact_email": "", "contact_name": "Mohab Khaled", "contact_orgnization": ""}]	active	85571fc5-9482-460e-89a6-164bfd936317
dc93bda7-13b4-48d1-b657-09a16ef724a0	publisher	no-limits publish	active	85571fc5-9482-460e-89a6-164bfd936317
a4ebe825-643d-4881-a92f-e8dda6c449c6	vertical_extent_datum		active	85571fc5-9482-460e-89a6-164bfd936317
c232ce11-1d90-4076-8a7f-ca3572b68982	publication_year	2022-06-21	active	85571fc5-9482-460e-89a6-164bfd936317
7607e799-9e3a-4c85-be1f-7086e7c75bbd	authors	[{"author_department": "", "author_email": "homab3@gmail.com", "author_name": "Mohab", "author_surname": "Khaled", "contact_same_as_author": "true"}]	active	85571fc5-9482-460e-89a6-164bfd936317
fc64b5cc-7375-4ffe-8e73-c248826140de	email	homab3@gmail.com	active	85571fc5-9482-460e-89a6-164bfd936317
1e23d749-3292-420b-b252-9991bace3d73	dataset_license_url		active	85571fc5-9482-460e-89a6-164bfd936317
be75f629-a8b6-44c5-b825-80fa2b6e7bf5	data_structure_category	structured	active	85571fc5-9482-460e-89a6-164bfd936317
bad8e400-c68a-421a-b420-e88c59401041	spatial	{"type": "Polygon", "coordinates": [[[16.4699, -22.1265], [32.8931, -22.1265], [32.8931, -34.8212], [16.4699, -34.8212], [16.4699, -22.1265]]]}	active	85571fc5-9482-460e-89a6-164bfd936317
66742ff0-d657-4cf8-bf6c-a576a36a09bf	wrc_project_number		active	85571fc5-9482-460e-89a6-164bfd936317
39b00d22-27af-4bce-afe4-4a03eb17fa16	did_author_or_contact_organization_collect_the_data	true	active	85571fc5-9482-460e-89a6-164bfd936317
a8cb5e94-aa2d-4b0a-96b0-597eacbe7c3a	wro_theme		active	85571fc5-9482-460e-89a6-164bfd936317
582a5ffd-a354-43fc-bbed-92519cf7896e	agreement	true	active	85571fc5-9482-460e-89a6-164bfd936317
eb166067-a389-467f-8110-75bfbb735b41	dataset_description	desc	active	85571fc5-9482-460e-89a6-164bfd936317
e037d08d-d22c-4c17-94ee-724ac16bfb7c	data_classification	static	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
466543c5-1b32-431b-918a-54f7c806037e	dataset_language		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
5d5dd3cd-a5b7-48cf-af1d-790f17e01883	minimum_maximum_extent	[{"maximum_vertical_extent": "", "minimum_vertical_extent": ""}]	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
7cf0580d-4f0a-4d11-a7cb-8b7c274e67c5	license	Open (Creative Commons)	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
8b5f5200-0301-4d88-9832-7a1bbb879148	publication_year	2022-06-20	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
662dc29c-d858-4d41-83e3-23b8bf7883af	wro_theme		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
bef040fe-017e-4031-a20f-d30ee4374415	keywords	metadata	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
cf9fa920-9caa-4022-877b-0922cb6c1568	wrc_project_number		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
0520f9c5-e813-4087-b2f7-ca21e8c30130	uploader_estimation_of_extent	raw	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
5c655602-1783-46bf-b7fb-e5046f4152dc	vertical_extent_datum		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
02fb4360-1f7b-41a2-a9f2-08a49a8c90cc	email	homab3@gmail.com	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
b508c6e1-72f6-46b7-9a38-b10ec6fc61b9	data_collection_organization		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
28ac9814-b879-4ce7-a824-008eccb0d6e9	publisher	no-limits publish	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
d2326b33-84dc-42a6-8551-2f8d3523a9e5	contact_person	[{"contact_department": "", "contact_email": "", "contact_name": "Mohab Khaled", "contact_orgnization": ""}]	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
1feef0f2-1423-4940-b3c7-8af578e96de2	dataset_license_url		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
8f4c05a0-9dd3-44f2-a568-575c26b11796	alternative_identifier		active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
38ee6983-bee1-4898-aeda-0034d032eb82	agreement	true	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
521abeaf-be27-4c04-8e43-c02bdaac1a4e	dataset_description	desc	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
e01be23c-36fc-4b1d-b6e0-b36b4b082779	data_structure_category	structured	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
1e2f6a1a-3e0c-4d1f-bd1d-3c3dee97e790	authors	[{"author_department": "", "author_email": "homab3@gmail.com", "author_name": "Mohab", "author_surname": "Khaled", "contact_same_as_author": "true"}]	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
9328d357-8c8e-43c5-9c3d-1bf7ce5e1daf	spatial	{"type": "Polygon", "coordinates": [[[16.4699, -22.1265], [32.8931, -22.1265], [32.8931, -34.8212], [16.4699, -34.8212], [16.4699, -22.1265]]]}	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
4c4b76e6-d17d-4635-b845-47f870fd11e8	did_author_or_contact_organization_collect_the_data	true	active	d0293dda-bffb-4cc0-a8c0-2a486d3828fa
\.


--
-- Data for Name: package_extra_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_extra_revision (id, key, value, revision_id, state, package_id, continuity_id, expired_id, revision_timestamp, expired_timestamp, current) FROM stdin;
\.


--
-- Data for Name: package_member; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_member (package_id, user_id, capacity, modified) FROM stdin;
\.


--
-- Data for Name: package_relationship; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_relationship (id, subject_package_id, object_package_id, type, comment, state) FROM stdin;
\.


--
-- Data for Name: package_relationship_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_relationship_revision (id, subject_package_id, object_package_id, type, comment, revision_id, continuity_id, state, expired_id, revision_timestamp, expired_timestamp, current) FROM stdin;
\.


--
-- Data for Name: package_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_revision (id, name, title, version, url, notes, author, author_email, maintainer, maintainer_email, revision_id, state, continuity_id, license_id, expired_id, revision_timestamp, expired_timestamp, current, type, owner_org, private, metadata_modified, creator_user_id, metadata_created) FROM stdin;
\.


--
-- Data for Name: package_tag; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_tag (id, state, package_id, tag_id) FROM stdin;
\.


--
-- Data for Name: package_tag_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.package_tag_revision (id, revision_id, state, package_id, tag_id, continuity_id, expired_id, revision_timestamp, expired_timestamp, current) FROM stdin;
\.


--
-- Data for Name: rating; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.rating (id, user_id, user_ip_address, rating, created, package_id) FROM stdin;
\.


--
-- Data for Name: resource; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.resource (id, url, format, description, "position", hash, state, extras, name, resource_type, mimetype, mimetype_inner, size, last_modified, cache_url, cache_last_updated, webstore_url, webstore_last_updated, created, url_type, package_id, metadata_modified) FROM stdin;
\.


--
-- Data for Name: resource_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.resource_revision (id, url, format, description, "position", revision_id, hash, state, continuity_id, extras, expired_id, revision_timestamp, expired_timestamp, current, name, resource_type, mimetype, mimetype_inner, size, last_modified, cache_url, cache_last_updated, webstore_url, webstore_last_updated, created, url_type, package_id) FROM stdin;
\.


--
-- Data for Name: resource_view; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.resource_view (id, resource_id, title, description, view_type, "order", config) FROM stdin;
\.


--
-- Data for Name: revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.revision (id, "timestamp", author, message, state, approved_timestamp) FROM stdin;
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: system_info; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.system_info (id, key, value, state) FROM stdin;
\.


--
-- Data for Name: system_info_revision; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.system_info_revision (id, key, value, revision_id, continuity_id, state, expired_id, revision_timestamp, expired_timestamp, current) FROM stdin;
\.


--
-- Data for Name: tag; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.tag (id, name, vocabulary_id) FROM stdin;
\.


--
-- Data for Name: task_status; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.task_status (id, entity_id, entity_type, task_type, key, value, state, error, last_updated) FROM stdin;
\.


--
-- Data for Name: term_translation; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.term_translation (term, term_translation, lang_code) FROM stdin;
\.


--
-- Data for Name: tracking_raw; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.tracking_raw (user_key, url, tracking_type, access_timestamp) FROM stdin;
\.


--
-- Data for Name: tracking_summary; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.tracking_summary (url, package_id, tracking_type, count, running_total, recent_views, tracking_date) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public."user" (id, name, apikey, created, about, password, fullname, email, reset_key, sysadmin, activity_streams_email_notifications, state, plugin_extras, image_url) FROM stdin;
2d8dc226-0d81-4113-a8a6-9d5a098bb529	default	743c3b2e-756e-4f1e-8043-27eaa92b557f	2022-06-20 01:25:20.064288	\N	$pbkdf2-sha512$25000$x1iLUapVKsW4994b49zbWw$70h6/k4P2nyrG.0d/enEkvUzchFYo/EhZmz1qwBmp.X1QUAlkNZe52nPW6nJG6DSeudIVxA2r177U.NqPwK//w	\N	\N	\N	t	f	active	\N	\N
3b76adea-3193-4483-8bde-ee8770366329	mohab	\N	2022-06-20 01:26:02.13185	\N	$pbkdf2-sha512$25000$eA8hJMT4v5fS.p.Tcq5V6g$QXRrDVT4gi83.lg4c9kEb0e8Mn17MzJzzeq5UH.W91fuNLU75PLw2pyaBcMKmwicV53CM8AHV1TmDEHcLJRayA	\N	mohab@localhost	\N	t	f	active	\N	\N
\.


--
-- Data for Name: user_following_dataset; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.user_following_dataset (follower_id, object_id, datetime) FROM stdin;
\.


--
-- Data for Name: user_following_group; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.user_following_group (follower_id, object_id, datetime) FROM stdin;
\.


--
-- Data for Name: user_following_user; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.user_following_user (follower_id, object_id, datetime) FROM stdin;
\.


--
-- Data for Name: vocabulary; Type: TABLE DATA; Schema: public; Owner: ckan_default
--

COPY public.vocabulary (id, name) FROM stdin;
\.


--
-- Name: system_info_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ckan_default
--

SELECT pg_catalog.setval('public.system_info_id_seq', 1, false);


--
-- Name: activity_detail activity_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.activity_detail
    ADD CONSTRAINT activity_detail_pkey PRIMARY KEY (id);


--
-- Name: activity activity_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: api_token api_token_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.api_token
    ADD CONSTRAINT api_token_pkey PRIMARY KEY (id);


--
-- Name: dashboard dashboard_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.dashboard
    ADD CONSTRAINT dashboard_pkey PRIMARY KEY (user_id);


--
-- Name: group_extra group_extra_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_extra
    ADD CONSTRAINT group_extra_pkey PRIMARY KEY (id);


--
-- Name: group_extra_revision group_extra_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_extra_revision
    ADD CONSTRAINT group_extra_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: group group_name_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public."group"
    ADD CONSTRAINT group_name_key UNIQUE (name);


--
-- Name: group group_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public."group"
    ADD CONSTRAINT group_pkey PRIMARY KEY (id);


--
-- Name: group_revision group_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_revision
    ADD CONSTRAINT group_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: harvest_gather_error harvest_gather_error_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_gather_error
    ADD CONSTRAINT harvest_gather_error_pkey PRIMARY KEY (id);


--
-- Name: harvest_job harvest_job_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_job
    ADD CONSTRAINT harvest_job_pkey PRIMARY KEY (id);


--
-- Name: harvest_log harvest_log_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_log
    ADD CONSTRAINT harvest_log_pkey PRIMARY KEY (id);


--
-- Name: harvest_object_error harvest_object_error_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object_error
    ADD CONSTRAINT harvest_object_error_pkey PRIMARY KEY (id);


--
-- Name: harvest_object_extra harvest_object_extra_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object_extra
    ADD CONSTRAINT harvest_object_extra_pkey PRIMARY KEY (id);


--
-- Name: harvest_object harvest_object_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object
    ADD CONSTRAINT harvest_object_pkey PRIMARY KEY (id);


--
-- Name: harvest_source harvest_source_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_source
    ADD CONSTRAINT harvest_source_pkey PRIMARY KEY (id);


--
-- Name: member member_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: member_revision member_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.member_revision
    ADD CONSTRAINT member_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: package_extent package_extent_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_extent
    ADD CONSTRAINT package_extent_pkey PRIMARY KEY (package_id);


--
-- Name: package_extra package_extra_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_extra
    ADD CONSTRAINT package_extra_pkey PRIMARY KEY (id);


--
-- Name: package_extra_revision package_extra_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_extra_revision
    ADD CONSTRAINT package_extra_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: package_member package_member_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_member
    ADD CONSTRAINT package_member_pkey PRIMARY KEY (package_id, user_id);


--
-- Name: package package_name_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package
    ADD CONSTRAINT package_name_key UNIQUE (name);


--
-- Name: package package_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package
    ADD CONSTRAINT package_pkey PRIMARY KEY (id);


--
-- Name: package_relationship package_relationship_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship
    ADD CONSTRAINT package_relationship_pkey PRIMARY KEY (id);


--
-- Name: package_relationship_revision package_relationship_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship_revision
    ADD CONSTRAINT package_relationship_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: package_revision package_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_revision
    ADD CONSTRAINT package_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: package_tag package_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag
    ADD CONSTRAINT package_tag_pkey PRIMARY KEY (id);


--
-- Name: package_tag_revision package_tag_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag_revision
    ADD CONSTRAINT package_tag_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: rating rating_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_pkey PRIMARY KEY (id);


--
-- Name: resource resource_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.resource
    ADD CONSTRAINT resource_pkey PRIMARY KEY (id);


--
-- Name: resource_revision resource_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.resource_revision
    ADD CONSTRAINT resource_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: resource_view resource_view_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.resource_view
    ADD CONSTRAINT resource_view_pkey PRIMARY KEY (id);


--
-- Name: revision revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.revision
    ADD CONSTRAINT revision_pkey PRIMARY KEY (id);


--
-- Name: system_info system_info_key_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info
    ADD CONSTRAINT system_info_key_key UNIQUE (key);


--
-- Name: system_info system_info_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info
    ADD CONSTRAINT system_info_pkey PRIMARY KEY (id);


--
-- Name: system_info_revision system_info_revision_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info_revision
    ADD CONSTRAINT system_info_revision_pkey PRIMARY KEY (id, revision_id);


--
-- Name: tag tag_name_vocabulary_id_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_name_vocabulary_id_key UNIQUE (name, vocabulary_id);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- Name: task_status task_status_entity_id_task_type_key_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.task_status
    ADD CONSTRAINT task_status_entity_id_task_type_key_key UNIQUE (entity_id, task_type, key);


--
-- Name: task_status task_status_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.task_status
    ADD CONSTRAINT task_status_pkey PRIMARY KEY (id);


--
-- Name: user_following_dataset user_following_dataset_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_dataset
    ADD CONSTRAINT user_following_dataset_pkey PRIMARY KEY (follower_id, object_id);


--
-- Name: user_following_group user_following_group_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_group
    ADD CONSTRAINT user_following_group_pkey PRIMARY KEY (follower_id, object_id);


--
-- Name: user_following_user user_following_user_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_user
    ADD CONSTRAINT user_following_user_pkey PRIMARY KEY (follower_id, object_id);


--
-- Name: user user_name_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_name_key UNIQUE (name);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: vocabulary vocabulary_name_key; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.vocabulary
    ADD CONSTRAINT vocabulary_name_key UNIQUE (name);


--
-- Name: vocabulary vocabulary_pkey; Type: CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.vocabulary
    ADD CONSTRAINT vocabulary_pkey PRIMARY KEY (id);


--
-- Name: guid_idx; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX guid_idx ON public.harvest_object USING btree (guid);


--
-- Name: harvest_job_id_idx; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX harvest_job_id_idx ON public.harvest_object USING btree (harvest_job_id);


--
-- Name: harvest_object_id_idx; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX harvest_object_id_idx ON public.harvest_object_extra USING btree (harvest_object_id);


--
-- Name: harvest_source_id_idx; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX harvest_source_id_idx ON public.harvest_object USING btree (harvest_source_id);


--
-- Name: idx_activity_detail_activity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_activity_detail_activity_id ON public.activity_detail USING btree (activity_id);


--
-- Name: idx_activity_object_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_activity_object_id ON public.activity USING btree (object_id, "timestamp");


--
-- Name: idx_activity_user_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_activity_user_id ON public.activity USING btree (user_id, "timestamp");


--
-- Name: idx_extra_grp_id_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_extra_grp_id_pkg_id ON public.member USING btree (group_id, table_id);


--
-- Name: idx_extra_id_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_extra_id_pkg_id ON public.package_extra USING btree (id, package_id);


--
-- Name: idx_extra_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_extra_pkg_id ON public.package_extra USING btree (package_id);


--
-- Name: idx_group_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_current ON public.group_revision USING btree (current);


--
-- Name: idx_group_extra_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_extra_current ON public.group_extra_revision USING btree (current);


--
-- Name: idx_group_extra_group_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_extra_group_id ON public.group_extra USING btree (group_id);


--
-- Name: idx_group_extra_period; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_extra_period ON public.group_extra_revision USING btree (revision_timestamp, expired_timestamp, id);


--
-- Name: idx_group_extra_period_group; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_extra_period_group ON public.group_extra_revision USING btree (revision_timestamp, expired_timestamp, group_id);


--
-- Name: idx_group_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_id ON public."group" USING btree (id);


--
-- Name: idx_group_name; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_name ON public."group" USING btree (name);


--
-- Name: idx_group_period; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_period ON public.group_revision USING btree (revision_timestamp, expired_timestamp, id);


--
-- Name: idx_group_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_group_pkg_id ON public.member USING btree (table_id);


--
-- Name: idx_member_continuity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_member_continuity_id ON public.member_revision USING btree (continuity_id);


--
-- Name: idx_package_continuity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_continuity_id ON public.package_revision USING btree (continuity_id);


--
-- Name: idx_package_creator_user_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_creator_user_id ON public.package USING btree (creator_user_id);


--
-- Name: idx_package_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_current ON public.package_revision USING btree (current);


--
-- Name: idx_package_extent_the_geom; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extent_the_geom ON public.package_extent USING gist (the_geom);


--
-- Name: idx_package_extra_continuity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_continuity_id ON public.package_extra_revision USING btree (continuity_id);


--
-- Name: idx_package_extra_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_current ON public.package_extra_revision USING btree (current);


--
-- Name: idx_package_extra_package_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_package_id ON public.package_extra_revision USING btree (package_id, current);


--
-- Name: idx_package_extra_period; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_period ON public.package_extra_revision USING btree (revision_timestamp, expired_timestamp, id);


--
-- Name: idx_package_extra_period_package; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_period_package ON public.package_extra_revision USING btree (revision_timestamp, expired_timestamp, package_id);


--
-- Name: idx_package_extra_rev_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_extra_rev_id ON public.package_extra_revision USING btree (revision_id);


--
-- Name: idx_package_group_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_current ON public.member_revision USING btree (current);


--
-- Name: idx_package_group_group_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_group_id ON public.member USING btree (group_id);


--
-- Name: idx_package_group_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_id ON public.member USING btree (id);


--
-- Name: idx_package_group_period_package_group; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_period_package_group ON public.member_revision USING btree (revision_timestamp, expired_timestamp, table_id, group_id);


--
-- Name: idx_package_group_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_pkg_id ON public.member USING btree (table_id);


--
-- Name: idx_package_group_pkg_id_group_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_group_pkg_id_group_id ON public.member USING btree (group_id, table_id);


--
-- Name: idx_package_period; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_period ON public.package_revision USING btree (revision_timestamp, expired_timestamp, id);


--
-- Name: idx_package_relationship_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_relationship_current ON public.package_relationship_revision USING btree (current);


--
-- Name: idx_package_resource_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_resource_id ON public.resource USING btree (id);


--
-- Name: idx_package_resource_package_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_resource_package_id ON public.resource USING btree (package_id);


--
-- Name: idx_package_resource_rev_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_resource_rev_id ON public.resource_revision USING btree (revision_id);


--
-- Name: idx_package_resource_url; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_resource_url ON public.resource USING btree (url);


--
-- Name: idx_package_tag_continuity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_continuity_id ON public.package_tag_revision USING btree (continuity_id);


--
-- Name: idx_package_tag_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_current ON public.package_tag_revision USING btree (current);


--
-- Name: idx_package_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_id ON public.package_tag USING btree (id);


--
-- Name: idx_package_tag_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_pkg_id ON public.package_tag USING btree (package_id);


--
-- Name: idx_package_tag_pkg_id_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_pkg_id_tag_id ON public.package_tag USING btree (tag_id, package_id);


--
-- Name: idx_package_tag_revision_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_revision_id ON public.package_tag_revision USING btree (id);


--
-- Name: idx_package_tag_revision_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_revision_pkg_id ON public.package_tag_revision USING btree (package_id);


--
-- Name: idx_package_tag_revision_pkg_id_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_revision_pkg_id_tag_id ON public.package_tag_revision USING btree (tag_id, package_id);


--
-- Name: idx_package_tag_revision_rev_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_revision_rev_id ON public.package_tag_revision USING btree (revision_id);


--
-- Name: idx_package_tag_revision_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_revision_tag_id ON public.package_tag_revision USING btree (tag_id);


--
-- Name: idx_package_tag_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_package_tag_tag_id ON public.package_tag USING btree (tag_id);


--
-- Name: idx_period_package_relationship; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_period_package_relationship ON public.package_relationship_revision USING btree (revision_timestamp, expired_timestamp, object_package_id, subject_package_id);


--
-- Name: idx_period_package_tag; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_period_package_tag ON public.package_tag_revision USING btree (revision_timestamp, expired_timestamp, package_id, tag_id);


--
-- Name: idx_pkg_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_id ON public.package USING btree (id);


--
-- Name: idx_pkg_lname; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_lname ON public.package USING btree (lower((name)::text));


--
-- Name: idx_pkg_name; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_name ON public.package USING btree (name);


--
-- Name: idx_pkg_revision_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_revision_id ON public.package_revision USING btree (id);


--
-- Name: idx_pkg_revision_name; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_revision_name ON public.package_revision USING btree (name);


--
-- Name: idx_pkg_revision_rev_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_revision_rev_id ON public.package_revision USING btree (revision_id);


--
-- Name: idx_pkg_sid; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_sid ON public.package USING btree (id, state);


--
-- Name: idx_pkg_slname; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_slname ON public.package USING btree (lower((name)::text), state);


--
-- Name: idx_pkg_sname; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_sname ON public.package USING btree (name, state);


--
-- Name: idx_pkg_stitle; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_stitle ON public.package USING btree (title, state);


--
-- Name: idx_pkg_suname; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_suname ON public.package USING btree (upper((name)::text), state);


--
-- Name: idx_pkg_title; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_title ON public.package USING btree (title);


--
-- Name: idx_pkg_uname; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_pkg_uname ON public.package USING btree (upper((name)::text));


--
-- Name: idx_rating_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_rating_id ON public.rating USING btree (id);


--
-- Name: idx_rating_package_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_rating_package_id ON public.rating USING btree (package_id);


--
-- Name: idx_rating_user_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_rating_user_id ON public.rating USING btree (user_id);


--
-- Name: idx_resource_continuity_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_resource_continuity_id ON public.resource_revision USING btree (continuity_id);


--
-- Name: idx_resource_current; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_resource_current ON public.resource_revision USING btree (current);


--
-- Name: idx_resource_period; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_resource_period ON public.resource_revision USING btree (revision_timestamp, expired_timestamp, id);


--
-- Name: idx_rev_state; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_rev_state ON public.revision USING btree (state);


--
-- Name: idx_revision_author; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_revision_author ON public.revision USING btree (author);


--
-- Name: idx_tag_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_tag_id ON public.tag USING btree (id);


--
-- Name: idx_tag_name; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_tag_name ON public.tag USING btree (name);


--
-- Name: idx_user_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_user_id ON public."user" USING btree (id);


--
-- Name: idx_user_name; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_user_name ON public."user" USING btree (name);


--
-- Name: idx_user_name_index; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX idx_user_name_index ON public."user" USING btree ((
CASE
    WHEN ((fullname IS NULL) OR (fullname = ''::text)) THEN name
    ELSE fullname
END));


--
-- Name: package_id_idx; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX package_id_idx ON public.harvest_object USING btree (package_id);


--
-- Name: term; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX term ON public.term_translation USING btree (term);


--
-- Name: term_lang; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX term_lang ON public.term_translation USING btree (term, lang_code);


--
-- Name: tracking_raw_access_timestamp; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_raw_access_timestamp ON public.tracking_raw USING btree (access_timestamp);


--
-- Name: tracking_raw_url; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_raw_url ON public.tracking_raw USING btree (url);


--
-- Name: tracking_raw_user_key; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_raw_user_key ON public.tracking_raw USING btree (user_key);


--
-- Name: tracking_summary_date; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_summary_date ON public.tracking_summary USING btree (tracking_date);


--
-- Name: tracking_summary_package_id; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_summary_package_id ON public.tracking_summary USING btree (package_id);


--
-- Name: tracking_summary_url; Type: INDEX; Schema: public; Owner: ckan_default
--

CREATE INDEX tracking_summary_url ON public.tracking_summary USING btree (url);


--
-- Name: activity_detail activity_detail_activity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.activity_detail
    ADD CONSTRAINT activity_detail_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES public.activity(id);


--
-- Name: api_token api_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.api_token
    ADD CONSTRAINT api_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: dashboard dashboard_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.dashboard
    ADD CONSTRAINT dashboard_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: group_extra group_extra_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_extra
    ADD CONSTRAINT group_extra_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: group_extra_revision group_extra_revision_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_extra_revision
    ADD CONSTRAINT group_extra_revision_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: group_extra_revision group_extra_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_extra_revision
    ADD CONSTRAINT group_extra_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: group_revision group_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.group_revision
    ADD CONSTRAINT group_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: harvest_gather_error harvest_gather_error_harvest_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_gather_error
    ADD CONSTRAINT harvest_gather_error_harvest_job_id_fkey FOREIGN KEY (harvest_job_id) REFERENCES public.harvest_job(id);


--
-- Name: harvest_job harvest_job_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_job
    ADD CONSTRAINT harvest_job_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.harvest_source(id);


--
-- Name: harvest_object_error harvest_object_error_harvest_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object_error
    ADD CONSTRAINT harvest_object_error_harvest_object_id_fkey FOREIGN KEY (harvest_object_id) REFERENCES public.harvest_object(id);


--
-- Name: harvest_object_extra harvest_object_extra_harvest_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object_extra
    ADD CONSTRAINT harvest_object_extra_harvest_object_id_fkey FOREIGN KEY (harvest_object_id) REFERENCES public.harvest_object(id);


--
-- Name: harvest_object harvest_object_harvest_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object
    ADD CONSTRAINT harvest_object_harvest_job_id_fkey FOREIGN KEY (harvest_job_id) REFERENCES public.harvest_job(id);


--
-- Name: harvest_object harvest_object_harvest_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object
    ADD CONSTRAINT harvest_object_harvest_source_id_fkey FOREIGN KEY (harvest_source_id) REFERENCES public.harvest_source(id);


--
-- Name: harvest_object harvest_object_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.harvest_object
    ADD CONSTRAINT harvest_object_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.package(id) DEFERRABLE;


--
-- Name: member member_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.member
    ADD CONSTRAINT member_group_id_fkey FOREIGN KEY (group_id) REFERENCES public."group"(id);


--
-- Name: member_revision member_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.member_revision
    ADD CONSTRAINT member_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: package_extra package_extra_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_extra
    ADD CONSTRAINT package_extra_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.package(id);


--
-- Name: package_extra_revision package_extra_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_extra_revision
    ADD CONSTRAINT package_extra_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: package_member package_member_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_member
    ADD CONSTRAINT package_member_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.package(id);


--
-- Name: package_member package_member_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_member
    ADD CONSTRAINT package_member_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: package_relationship package_relationship_object_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship
    ADD CONSTRAINT package_relationship_object_package_id_fkey FOREIGN KEY (object_package_id) REFERENCES public.package(id);


--
-- Name: package_relationship_revision package_relationship_revision_continuity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship_revision
    ADD CONSTRAINT package_relationship_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES public.package_relationship(id);


--
-- Name: package_relationship_revision package_relationship_revision_object_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship_revision
    ADD CONSTRAINT package_relationship_revision_object_package_id_fkey FOREIGN KEY (object_package_id) REFERENCES public.package(id);


--
-- Name: package_relationship_revision package_relationship_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship_revision
    ADD CONSTRAINT package_relationship_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: package_relationship_revision package_relationship_revision_subject_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship_revision
    ADD CONSTRAINT package_relationship_revision_subject_package_id_fkey FOREIGN KEY (subject_package_id) REFERENCES public.package(id);


--
-- Name: package_relationship package_relationship_subject_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_relationship
    ADD CONSTRAINT package_relationship_subject_package_id_fkey FOREIGN KEY (subject_package_id) REFERENCES public.package(id);


--
-- Name: package_revision package_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_revision
    ADD CONSTRAINT package_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: package_tag package_tag_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag
    ADD CONSTRAINT package_tag_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.package(id);


--
-- Name: package_tag_revision package_tag_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag_revision
    ADD CONSTRAINT package_tag_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: package_tag_revision package_tag_revision_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag_revision
    ADD CONSTRAINT package_tag_revision_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- Name: package_tag package_tag_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.package_tag
    ADD CONSTRAINT package_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id);


--
-- Name: rating rating_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.package(id);


--
-- Name: rating rating_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.rating
    ADD CONSTRAINT rating_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: resource_revision resource_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.resource_revision
    ADD CONSTRAINT resource_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: resource_view resource_view_resource_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.resource_view
    ADD CONSTRAINT resource_view_resource_id_fkey FOREIGN KEY (resource_id) REFERENCES public.resource(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: system_info_revision system_info_revision_continuity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info_revision
    ADD CONSTRAINT system_info_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES public.system_info(id);


--
-- Name: system_info_revision system_info_revision_revision_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.system_info_revision
    ADD CONSTRAINT system_info_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES public.revision(id);


--
-- Name: tag tag_vocabulary_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_vocabulary_id_fkey FOREIGN KEY (vocabulary_id) REFERENCES public.vocabulary(id);


--
-- Name: user_following_dataset user_following_dataset_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_dataset
    ADD CONSTRAINT user_following_dataset_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public."user"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_following_dataset user_following_dataset_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_dataset
    ADD CONSTRAINT user_following_dataset_object_id_fkey FOREIGN KEY (object_id) REFERENCES public.package(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_following_group user_following_group_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_group
    ADD CONSTRAINT user_following_group_group_id_fkey FOREIGN KEY (object_id) REFERENCES public."group"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_following_group user_following_group_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_group
    ADD CONSTRAINT user_following_group_user_id_fkey FOREIGN KEY (follower_id) REFERENCES public."user"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_following_user user_following_user_follower_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_user
    ADD CONSTRAINT user_following_user_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES public."user"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_following_user user_following_user_object_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ckan_default
--

ALTER TABLE ONLY public.user_following_user
    ADD CONSTRAINT user_following_user_object_id_fkey FOREIGN KEY (object_id) REFERENCES public."user"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

