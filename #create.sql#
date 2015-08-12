CREATE DATABASE UWNet;
USE UWNet;

CREATE TABLE InputQueue(
	id INT NOT NULL AUTO_INCREMENT,
	mpwr INT NOT NULL,
	lpwr INT NOT NULL,
	ppwr INT NOT NULL,
	mbkn INT NOT NULL,
	lbkn INT NOT NULL,
	pbkn INT NOT NULL,
	mmod INT NOT NULL,
	lmod INT NOT NULL,
	pmod INT NOT NULL,
	testData VARCHAR(1024),
	email VARCHAR(128),
	PRIMARY KEY(id)
);

CREATE TABLE Results(
	experimentID INT NOT NULL,
	parameters VARCHAR(128),
	results VARCHAR(128),
	done BOOL,
	FOREIGN KEY(experimentID) REFERENCES InputQueue(id)
);
