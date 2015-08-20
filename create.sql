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
	exitStatus INT DEFAULT NULL,
	emailSent BOOL DEFAULT FALSE,
	PRIMARY KEY(id)
);

CREATE TABLE Results(
	experimentID INT NOT NULL,

	-- TODO:
	--	1) possibly replace 'parameters' with 3 columns:
	--		- 'pwr', 'bkn', 'mod'
	-- 	2) possibly replace 'results':
	--		- maybe have datetime columns for start time, end time

	parameters VARCHAR(2048),
	results VARCHAR(2048),
	FOREIGN KEY(experimentID) REFERENCES InputQueue(id)
);
