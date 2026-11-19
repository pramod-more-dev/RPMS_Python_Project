
USE recruitment_portal;

-- 1. Candidate Count by Technology
SELECT primary_technology, COUNT(*) AS total_candidates
FROM candidates
GROUP BY primary_technology
ORDER BY total_candidates DESC;

-- 2. Open Jobs by Company
SELECT c.company_name, COUNT(j.job_id) AS open_jobs
FROM companies c
LEFT JOIN jobs j
    ON c.company_id = j.company_id
    AND j.status = 'OPEN'
GROUP BY c.company_id, c.company_name
ORDER BY open_jobs DESC;

-- 3. Applications by Status
SELECT application_status, COUNT(*) AS total_applications
FROM applications
GROUP BY application_status
ORDER BY total_applications DESC;


-- 4. Recruitment Funnel
SELECT
    COUNT(*) AS total_applications,
    SUM(application_status = 'APPLIED') AS applied,
    SUM(application_status = 'ELIGIBILITY_VERIFIED') AS eligibility_verified,
    SUM(application_status = 'SHORTLISTED') AS shortlisted,
    SUM(application_status = 'INTERVIEW_SCHEDULED') AS interview_scheduled,
    SUM(application_status = 'INTERVIEWED') AS interviewed,
    SUM(application_status = 'SELECTED') AS selected,
    SUM(application_status = 'OFFERED') AS offered,
    SUM(application_status = 'REJECTED') AS rejected
FROM applications;


-- 5. Company-wise Placements
SELECT c.company_name, COUNT(p.placement_id) AS total_placements
FROM companies c
LEFT JOIN placements p ON c.company_id = p.company_id
GROUP BY c.company_id, c.company_name
ORDER BY total_placements DESC;

-- 6. Technology-wise Placements
SELECT ca.primary_technology, COUNT(p.placement_id) AS total_placements
FROM candidates ca
JOIN placements p ON ca.candidate_id = p.candidate_id
GROUP BY ca.primary_technology
ORDER BY total_placements DESC;

-- 7. Pending Interviews
SELECT COUNT(*) AS pending_interviews
FROM interview_rounds
WHERE status = 'SCHEDULED';

-- 8. Offer-to-Joining Conversion
SELECT
    COUNT(*) AS total_placements,
    SUM(joining_status = 'JOINED') AS joined_candidates,
    ROUND(
        100.0 * SUM(joining_status = 'JOINED') / NULLIF(COUNT(*), 0),
        2
    ) AS joining_conversion_percentage
FROM placements;

-- 9. Job Aging
SELECT
    job_code,
    job_title,
    posted_date,
    DATEDIFF(CURDATE(), posted_date) AS job_age_days
FROM jobs
WHERE status = 'OPEN'
ORDER BY job_age_days DESC;

-- 10. Recruiter Performance
SELECT
    u.full_name AS recruiter_name,
    COUNT(a.application_id) AS total_applications
FROM users u
LEFT JOIN applications a
    ON u.user_id = a.assigned_recruiter_id
GROUP BY u.user_id, u.full_name
ORDER BY total_applications DESC;
