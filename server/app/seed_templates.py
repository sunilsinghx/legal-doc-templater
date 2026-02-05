from sqlalchemy.orm import Session
from app.models import Template
from app.database import SessionLocal
from app.services.gemini import embed_text


SEED_TEMPLATES = [
    {
        "tags": ["confidentiality", "nda", "business relationship"],
        "title": "MUTUAL NON.pdf",
        "variables": [
            {
                "key": "effective_date",
                "label": "Effective Date",
                "description": "The date on which the agreement becomes legally binding.",
                "example": "January 20, 2026",
                "required": True,
                "dtype": "date",
            },
            {
                "key": "disclosing_party_name",
                "label": "Disclosing Party Name",
                "description": "The name of the party disclosing confidential information.",
                "example": "Acme Tech Solutions",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "disclosing_party_address",
                "label": "Disclosing Party Address",
                "description": "The physical address of the party disclosing confidential information.",
                "example": "456 Innovation Way, Bangalore, Karnataka",
                "required": False,
                "dtype": "string",
            },
            {
                "key": "receiving_party_name",
                "label": "Receiving Party Name",
                "description": "The name of the party receiving confidential information.",
                "example": "Arjun Mehra",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "receiving_party_address",
                "label": "Receiving Party Address",
                "description": "The physical address of the party receiving confidential information.",
                "example": "789 Maple Street, Mumbai, Maharashtra",
                "required": False,
                "dtype": "string",
            },
            {
                "key": "purpose_of_agreement",
                "label": "Purpose of Agreement",
                "description": "The business relationship or project for which confidential information is being shared.",
                "example": "Project CyberCore",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "confidentiality_period",
                "label": "Confidentiality Period",
                "description": "The duration for which the shared information must be protected as confidential.",
                "example": "3 years",
                "required": True,
                "dtype": "duration",
            },
            {
                "key": "governing_law",
                "label": "Governing Law",
                "description": "The jurisdiction whose laws will interpret the agreement.",
                "example": "India",
                "required": True,
                "dtype": "string",
            },
        ],
        "body_md": """# MUTUAL NON-DISCLOSURE AGREEMENT
This Mutual Non-Disclosure Agreement (“Agreement”) is entered into as of **{{effective_date}}** (the “Effective Date”) by and between:

**DISCLOSING PARTY:**  
{{disclosing_party_name}}  
Located at {{disclosing_party_address}}

**RECEIVING PARTY:**  
{{receiving_party_name}}  
An individual residing at {{receiving_party_address}}

## 1. Purpose
The parties wish to explore a business relationship regarding **{{purpose_of_agreement}}**.

## 2. Confidential Information
All technical, business, and proprietary information disclosed under this Agreement shall be treated as confidential and protected for a period of **{{confidentiality_period}}**.

## 3. Governing Law
This Agreement shall be governed by and construed in accordance with the laws of **{{governing_law}}**.

---

**Signature:** __________________________  
**Name:** {{disclosing_party_name}}  
**Date:** __________________________  

**Signature:** __________________________  
**Name:** {{receiving_party_name}}  
**Date:** __________________________  

        
        """,
    },
    {
        "body": "# INSURANCE POLICY DOCUMENT\n\n## PART A\n\n**Issued By:** {{party_a_name}}\n\n**Issued To:** {{party_b_name}}\n\n**Subject Matter:** {{subject_matter_description}}\n\n**Effective Date:** {{effective_date}}\n\n---\n\nDear Policyholder,\n\nWe are pleased to forward the Policy Document comprising multiple parts, along with related customer information and benefit details.\n\nYou are requested to carefully review the information stated in the Schedule of the Policy and the benefits available under the Policy. Certain options, including riders, may be available under this Policy. It is important to note any such options mentioned in the Policy Document, as they may be exercised only in the prescribed manner and within the stipulated time limits.\n\n---\n\n## FREE LOOK PERIOD\n\nYou are advised to review the terms and conditions of the Policy. If you disagree with any of the terms and conditions, you may return the Policy within a period of thirty days from the date of receipt of the Policy Document, whether received electronically or in physical form, whichever is earlier, stating the reasons for objection or disagreement.\n\nUpon receipt of the returned Policy, the Policy shall be cancelled and the consideration amount paid shall be refunded after deducting proportionate risk charges for the period of coverage, applicable rider charges, medical examination charges, and statutory charges, if any.\n\n**Consideration Amount:** {{consideration_amount}}\n\n---\n\n## COMPLAINTS AND GRIEVANCE REDRESSAL\n\nIn case of any complaint or grievance, you may approach the designated service office or the grievance redressal authority as notified from time to time.\n\nIf any error is noticed in this Policy Document, the Policy may be returned for necessary corrections.\n\n---\n\nThanking you,\n\nYours faithfully,\n\nAuthorized Signatory\n\n---\n\n## ADDITIONAL INFORMATION\n\n1. **Change of Address:** Any change in address should be promptly communicated to the servicing office.\n\n2. **Assignment:** Assignment of the Policy shall be governed by applicable law.\n\n---\n\n**Governing Jurisdiction:** {{governing_jurisdiction}}\n",
        "variables": [
            {
                "key": "party_a_name",
                "label": "Party A Name",
                "description": "The name of the issuing insurer or policy provider.",
                "example": "Insurance Provider Name",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "party_b_name",
                "label": "Party B Name",
                "description": "The name of the policyholder or insured party.",
                "example": "Policyholder Name",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "subject_matter_description",
                "label": "Subject Matter Description",
                "description": "Description of the insurance coverage or plan.",
                "example": "Life insurance savings policy",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "effective_date",
                "label": "Effective Date",
                "description": "The date on which the policy becomes effective.",
                "example": "Policy commencement date",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "consideration_amount",
                "label": "Consideration Amount",
                "description": "The premium or amount paid for the insurance coverage.",
                "example": "Premium amount",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "governing_jurisdiction",
                "label": "Governing Jurisdiction",
                "description": "The legal jurisdiction governing the policy.",
                "example": "Applicable governing law",
                "required": True,
                "dtype": "string",
            },
        ],
        "similarity_tags": ["insurance_policy", "life_insurance", "policy_document"],
    },
    {
        "title": "Employment Agreement",
        "similarity_tags": ["employment", "hr", "job_contract"],
        "body": """
        # EMPLOYMENT AGREEMENT

This Employment Agreement (“Agreement”) is entered into on **{{effective_date}}** between **{{employer_name}}**, located at **{{employer_address}}**, and **{{employee_name}}**.

## 1. Position
The Employee shall serve as **{{job_title}}**.

## 2. Start Date
{{start_date}}

## 3. Compensation
{{salary_details}}

## 4. Confidentiality
The Employee agrees to maintain confidentiality of all proprietary and sensitive information.

## 5. Governing Law
This Agreement shall be governed by and construed in accordance with the laws of **{{governing_law}}**.

---

**Employer Signature:** ___________________________  
**Date:** ___________________________

**Employee Signature:** ___________________________  
**Date:** ___________________________

""",
        "variables": [
            {
                "key": "effective_date",
                "label": "Effective Date",
                "example": "January 1, 2026",
                "required": True,
                "dtype": "date",
            },
            {
                "key": "employer_name",
                "label": "Employer Name",
                "example": "ABC Technologies Pvt Ltd",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "employer_address",
                "label": "Employer Address",
                "example": "Bangalore, India",
                "required": False,
                "dtype": "string",
            },
            {
                "key": "employee_name",
                "label": "Employee Name",
                "example": "Rahul Sharma",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "job_title",
                "label": "Job Title",
                "example": "Software Engineer",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "start_date",
                "label": "Start Date",
                "example": "February 1, 2026",
                "required": True,
                "dtype": "date",
            },
            {
                "key": "salary_details",
                "label": "Salary Details",
                "example": "₹15,00,000 per annum",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "governing_law",
                "label": "Governing Law",
                "example": "India",
                "required": True,
                "dtype": "string",
            },
        ],
    },
    {
        "title": "Service Agreement",
        "similarity_tags": ["service", "contract", "business"],
        "body": """
        # SERVICE AGREEMENT

This Service Agreement (“Agreement”) is made on **{{effective_date}}** between **{{service_provider_name}}** and **{{client_name}}**.

## 1. Services
{{service_description}}

## 2. Term
{{agreement_term}}

## 3. Payment
{{payment_terms}}

## 4. Termination
Either party may terminate this Agreement with **{{termination_notice}}** notice.

## 5. Governing Law
This Agreement shall be governed by and construed in accordance with the laws of **{{governing_law}}**.

---

**Signed by both parties below.**

**Service Provider:** ___________________________  
**Date:** ___________________________

**Client:** ___________________________  
**Date:** ___________________________

""",
        "variables": [
            {
                "key": "effective_date",
                "label": "Effective Date",
                "example": "March 10, 2026",
                "required": True,
                "dtype": "date",
            },
            {
                "key": "service_provider_name",
                "label": "Service Provider Name",
                "example": "XYZ Consulting",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "client_name",
                "label": "Client Name",
                "example": "Global Enterprises Ltd",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "service_description",
                "label": "Service Description",
                "example": "IT consulting services",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "agreement_term",
                "label": "Agreement Term",
                "example": "12 months",
                "required": True,
                "dtype": "duration",
            },
            {
                "key": "payment_terms",
                "label": "Payment Terms",
                "example": "Monthly invoicing",
                "required": True,
                "dtype": "string",
            },
            {
                "key": "termination_notice",
                "label": "Termination Notice",
                "example": "30 days",
                "required": True,
                "dtype": "duration",
            },
            {
                "key": "governing_law",
                "label": "Governing Law",
                "example": "India",
                "required": True,
                "dtype": "string",
            },
        ],
    },
]


def seed_templates(db: Session):
    for tpl in SEED_TEMPLATES:
        exists = db.query(Template).filter(Template.title == tpl["title"]).first()

        if exists:
            continue

        embedding_text = " ".join([tpl["title"], " ".join(tpl["tags"])])

        embedding = embed_text(embedding_text)

        template = Template(
            title=tpl["title"],
            body=tpl["body"],
            variables=tpl["variables"],
            tags=tpl["similarity_tags"],
            embedding=embedding,
        )

        db.add(template)

    db.commit()


def run():
    db = SessionLocal()
    try:
        seed_templates(db)
        print("✅ Templates seeded successfully")
    finally:
        db.close()


if __name__ == "__main__":
    run()
