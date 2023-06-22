CREATE TABLE users (
	id integer PRIMARY KEY AUTOINCREMENT,
	email text,
	nickname text,
	password text,
	token text
);

CREATE TABLE uploaded_files (
	id integer PRIMARY KEY AUTOINCREMENT,
	user_id integer,
	date datetime,
	file text,
	range_start datetime,
	range_end datetime
);





