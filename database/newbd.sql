CREATE TABLE users (
	id integer PRIMARY KEY AUTOINCREMENT,
	email string,
	nickname string,
	password string,
	token string
);

CREATE TABLE uploaded_files (
	id integer PRIMARY KEY AUTOINCREMENT,
	user_id integer,
	date datetime,
	directory_id integer,
	file text,
	range_start datetime,
	range_end datetime
);

CREATE TABLE directories (
	id integer PRIMARY KEY AUTOINCREMENT,
	user_id integer,
	name_directory text
);




