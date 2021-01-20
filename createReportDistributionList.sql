USE JupiterCustomData;
DROP TABLE clincialother.ReportDistribution;

CREATE TABLE clincialother.ReportDistribution (
    ReportUserID int IDENTITY(1,1) ,
	Report varchar(250),
	EmailTo varchar(100) NOT NULL,
    UpdatedBy varchar(200) DEFAULT SYSTEM_USER,
	CreatedWhen datetime2
			CONSTRAINT DF_ReportDistribution_Created DEFAULT (SYSDATETIME()),
	ModifiedWhen datetime2,
	CONSTRAINT PK_Report 
			PRIMARY KEY (Report, EmailTo),
   CONSTRAINT UC_ReportEmail UNIQUE (Report,EmailTo)
);


DROP TABLE clincialother.ReportDescription;

CREATE TABLE clincialother.ReportDescription (
    ReportID int IDENTITY(1,1) ,
	Report varchar(250) NOT NULL PRIMARY KEY,
	ReportDescription varchar(2000) NULL,
    UpdatedBy varchar(200) DEFAULT SYSTEM_USER,
	CreatedWhen datetime2
			CONSTRAINT DF_ReportDescription_Created DEFAULT (SYSDATETIME()),
	ModifiedWhen datetime2,
   CONSTRAINT UC_Report UNIQUE (Report)
);

CREATE TRIGGER updateModified_ReportDistribution
ON clincialother.ReportDistribution
AFTER UPDATE 
AS
   UPDATE clincialother.ReportDistribution
   SET ModifiedWhen = SYSDATETIME()
   FROM Inserted i
   WHERE clincialother.ReportDistribution.ReportUserID = i.ReportUserID;

CREATE TRIGGER updateModified_ReportDescription
ON clincialother.ReportDescription
AFTER UPDATE 
AS
   UPDATE clincialother.ReportDescription
   SET ModifiedWhen = SYSDATETIME()
   FROM Inserted i
   WHERE clincialother.ReportDescription.Report = i.Report;


truncate table clincialother.ReportDistribution

INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'miz9013@nyp.org')  
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'jue9032@nyp.org')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'caw9095@nyp.org')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'kn2174@cumc.columbia.edu')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'evs2008@med.cornell.edu')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'amd9086@nyp.org')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('ClarityUpdate' , 'kib9034@nyp.org')

INSERT INTO clincialother.ReportDescription (Report, ReportDescription) VALUES ('ClarityUpdate' , 'This report checks the previous day''s list of tables in Jupiter''s Clarity DB against the current list of tables in Jupiter Clarity. If there are new tables it sends an email to the distribution list with the names of the new tables.')


SELECT * FROM JupiterCustomData.clincialother.ReportDistribution
SELECT * FROM JupiterCustomData.clincialother.ReportDescription


UPDATE clincialother.ReportDescription SET ReportDescription = 'This report checks the previous day''s list of tables in Jupiter''s Clarity database against the current list of tables in Jupiter Clarity. If there are new tables it sends an email to the distribution list with the names of the new tables.' WHERE Report = 'ClarityUpdate'



INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('SerologyTest' , 'miz9013@nyp.org')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('SerologyTest' , 'mdh9011@nyp.org')
INSERT INTO clincialother.ReportDescription (Report, ReportDescription) VALUES ('SerologyTest' , 'Serology Outputs')


INSERT INTO clincialother.ReportDescription (Report, ReportDescription) VALUES ('Demo' , 'This is a demo report')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('Demo' , 'miz9013@nyp.org')
INSERT INTO clincialother.ReportDistribution (Report, EmailTo) VALUES ('Demo' , 'rop9001@nyp.org')

DELETE FROM clincialother.ReportDistribution WHERE Report = 'Demo' and Emailto = 'miz9013@nyp.org'

SELECT ReportUserID, count(ReportUserID) n FROM clincialother.ReportDistribution group by ReportUserID order by n



DELETE FROM JupiterCustomData.clincialother.ReportDescription WHERE Report = 'Demo2' 