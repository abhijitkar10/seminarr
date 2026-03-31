# Problem Overview
In modern enterprises, identity compromise is the leading cause of security breaches. Traditional rule-based access monitoring fails to detect sophisticated attacks where adversaries mimic legitimate user behavior. This challenges students to build an AI-powered anomaly detection system that identifies suspicious access patterns indicating:
- Compromised credentials
- Insider threats
- Privilege abuse
- Account takeover attacks
## Problem Statement
### Objective: 
Develop a Proof-of-Concept (PoC) system that uses machine learning to detect anomalous user access behaviour in real-time from authentication and authorisation logs.
### Core Requirements
Students must build a system that:
1.	Ingests and processes authentication/authorisation logs (login times, locations, resources accessed, failed attempts)
2.	Establishes baseline behaviour profiles for normal user activities
3.	Detects anomalies using unsupervised/semi-supervised ML algorithms
4.	Generates risk scores and alerts for suspicious activities
5.	Visualizes findings through an interactive dashboard
6.	Provides explanations for why specific activities are flagged as anomalous

### Expected Deliverables
  Component              Description
- Data Pipeline		    Log ingestion, parsing, and feature engineering
- ML Model		        Trained anomaly detection model with evaluation metrics
- Alert System		    Real-time risk scoring and notification mechanism
- Dashboard		        Web-based interface showing user activities, anomalies, and trends
- Documentation	        Architecture diagram, model selection rationale, deployment guide
- Presentation		    10-minute demo showcasing the PoC capabilities

