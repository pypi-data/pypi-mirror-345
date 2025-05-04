import pandas as pd
from .logger import Logger
from sqlalchemy import create_engine
from typing import Literal

# This is Version 1.0.0
# View Lists
viewList = Literal[
	'AssumptionLog','CorpSchedule','CorpSchedule2WellEvent','CorpScheduleVersion','DesignConstraint','EconomicCase','EconomicCaseCapexResult','EconomicCaseParametersByFluid','EconomicCasePrdResult','EconomicCaseResult','EconomicCaseVersion','EconomicCaseWellEventCountResult','Facility','FacilityCapacity','Field','FluidType','HierarchicalOrg','InvestmentCode','IssueLog','LessonLearned','Milestone','MilestoneVersion','MilestoneVersion2Strategy','OtherInvestment','OtherInvestmentMilestone','PrdZone','Project','Project2ChanceOfCommerciality','Project2features','Project2Partner','Project2ProductionShare','Project2ReservoirTarget','Project2User2Role','ProjectCharter','ProjectDeliverable','ProjectPhase','ProjectRoadMap','ProjectSchedule','ProjectSchedule2WellEvent','ProjectSchedule2WellTieIn','ProjectWellMilestone','ProjectWellMilestone2Reservoir','PublishedCost','PublishedCostCurve','PublishedEURandReservesByWell','PublishedWellProduction','Reservoir','Reservoir2Fluid','Risk','StaffPlan','Stakeholder','Strategy','Strategy2Guidelines','Strategy2Zone','ValueDriver','WellCurve','WellCurveFactor','WellCurveFluid','WellCurveParametric','WellCurveValue','WellCurveVersion','WellDesign','WellDesignCost','WellDesignVersion','WellMaster','Zone','Zone2ReservoirTarget',
    ]

class DBConnection:
    _instance = None

    def __new__(cls,username:str, password:str, server:str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            database_name = 'MirKusAnalytics'
            dbConectionStringSQLAlchemy = f"mssql+pyodbc://{username}:{password}@{server}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server"
            cls._instance._initialize(cncString=dbConectionStringSQLAlchemy)
        return cls._instance

    def _initialize(self, cncString: str):
        self.logger = Logger('DB Connection')
        try:
            self._conection_sqlAlchemy = create_engine(cncString)
            self._conection_sqlAlchemy.connect()
            self.logger.info(f" ----------> Database successfully connected!")
        except Exception as error:
            self.logger.error(error)

    def get(self, sqlScript:str) -> pd.DataFrame:
        try:
            output: pd.DataFrame = pd.read_sql(sqlScript, self._conection_sqlAlchemy)
            self.logger.info(f"get(pd.read_sql): {sqlScript}")
        except Exception as error:
                self.logger.error(error)
        return output

    def getMirKusData(self, view: viewList)->pd.DataFrame:
        sql = 'Select * from [da_view].[' + view + ']'
        return self.get(sql)    

