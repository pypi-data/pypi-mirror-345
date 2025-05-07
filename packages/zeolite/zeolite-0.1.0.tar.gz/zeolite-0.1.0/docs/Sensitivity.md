Data Classification System

## 1. Highly Sensitive Data

Data with the highest level of sensitivity that requires the most stringent protection measures. This includes special
category data as defined by privacy regulations, such as information about health conditions that may lead to
stigmatization, mental health diagnoses, sexual health information, genetic data, and substance abuse records. Requires
explicit consent, encryption at rest and in transit, strict access controls, comprehensive audit logging, and special
authorization for processing.

## 2. Confidential Data

Health or social care data requiring robust protection but not falling into the highest sensitivity category. This
includes health measurements, treatment details, medication information, and care notes. Requires strong access
controls, encryption, audit trails, and justification for processing. Access should be limited to those with a clear
need-to-know basis.

## 3. Identifiable Data

Data elements that directly identify an individual. This includes names, addresses, phone numbers, email addresses,
account numbers, and government-issued identification numbers like Social Security Numbers. These elements should be
subject to access controls, data minimization principles, and pseudonymization where possible. Should never be shared or
exposed without appropriate safeguards.

## 4. Potentially Identifiable Data

Data elements that may not directly identify an individual but could do so when combined with other information. This
includes date of birth, age, zip/postal codes, gender, ethnicity, and occupation. Requires careful handling when used in
datasets, potentially using techniques like aggregation, generalization, or k-anonymity for public use to prevent
re-identification.

## 5. Limited Sensitivity Data

Operational or administrative data with minimal personal information but still requires protection. This includes
appointment dates, service categories, department codes, and insurance information. Should follow standard data
protection practices and appropriate access controls. Generally lower risk but still subject to organizational data
protection policies.

## 6. Non-Sensitive Data

Non-identifiable metadata or system information that poses minimal privacy risk. This includes form version numbers,
facility identifiers, service type codes, and similar technical or operational metadata. Subject to minimal restrictions
and can be used for most purposes including analytics, reporting, and operational processes without special
considerations.