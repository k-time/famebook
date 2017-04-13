CREATE TABLE Users (
	username varchar(50), 
	password varchar(50), 
	user_id int, 
	PRIMARY KEY (user_id)
);
CREATE TABLE User_Follows(
	user_id int, 
	people_id int, 
	PRIMARY KEY (user_id, people_id)
	FOREIGN KEY (user_id) REFERENCES Users
		ON DELETE NO ACTION
	FOREIGN KEY (people_id) REFERENCES Notable_People_Adder
		ON DELETE NO ACTION
);
CREATE TABLE News(
	news_id int, 
	source text, 
	content text,
	datetime timestamp, //added this
	PRIMARY KEY (news_id),
);
CREATE TABLE Notable_People_Has(
	people_id int,
	news_id int, 
	PRIMARY KEY (people_id, news_id),
	FOREIGN KEY (people_id) REFERENCES Notable_People_Adder
		ON DELETE NO ACTION,
	FOREIGN KEY (news_id) REFERENCES News
		ON DELETE NO ACTION
);
CREATE TABLE Notable_People_Adder(
	people_id int,
	name text, 
	net_worth int,
	instagram_username text, 
	twitter_username text, 
	facebook_page_name text,
	user_id int NOT NULL,
	PRIMARY KEY (people_id),
	FOREIGN KEY (user_id) REFERENCES Users
		ON DELETE NO ACTION
);
CREATE TABLE Weekly_Leaderboard_Ranks(
	week date,
	people_id int NOT NULL,
	percent_increase int,
	position int,
	CHECK (position>0 and position <11),
	PRIMARY KEY (week, people_id),
	FOREIGN KEY (people_id) REFERENCES Notable_People_Adder
		ON DELETE NO ACTION
);
CREATE TABLE Notable_People_Rating(
	rating_week date,
	rating_average double,
	people_id int,
	CHECK (rating_average>0 and rating_average<6),
	PRIMARY KEY (rating_week, people_id),
	FOREIGN KEY (people_id) REFERENCES Notable_People_Adder
		ON DELETE NO ACTION 
);			
CREATE TABLE Submits(
	user_id int,
	rating_week date, 
	people_id int NOT NULL,
	rating_level int, 
	PRIMARY KEY (user_id, rating_week, people_id),
	FOREIGN KEY (user_id) REFERENCES Users
		ON DELETE NO ACTION, 
	FOREIGN KEY (people_id) REFERENCES Notable_People_Adder
		ON DELETE NO ACTION
);
