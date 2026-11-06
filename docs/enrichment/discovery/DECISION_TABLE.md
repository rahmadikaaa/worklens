# WORKLENS — Decision Table for Enrichment & Benefit Generation

> **Status:** Discovery Baseline Reference  
> **Applicable Pipeline:** WORKLENS Deterministic Operational Enrichment  

---

## 1. Decision Table: Benefit Template Selection

Tabel keputusan berikut mendefinisikan pembentukan kalimat naratif `Benefit` berdasarkan kombinasi `Status Triggered`, `Workload Range`, dan `Event Per Month`:

| Condition: Status Triggered | Condition: Workload Range | Condition: Event Per Month | Resulting Benefit Template Structure |
|---|---|---|---|
| `Fully Automated` | $\text{Workload} = 0$ | Any | `Eliminates manual intervention time and accelerates system recovery {tool_clause} through {action_phrase}.` |
| `Fully Automated` | $0 < \text{Workload} < 60$ | $= 1$ | `Eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event) {tool_clause} through {action_phrase}.` |
| `Fully Automated` | $0 < \text{Workload} < 60$ | $> 1$ | `Eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.` |
| `Fully Automated` | $\text{Workload} \ge 60$ | $= 1$ | `Eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event) {tool_clause} through {action_phrase}.` |
| `Fully Automated` | $\text{Workload} \ge 60$ | $> 1$ | `Eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.` |
| `Not Yet Triggered Automated` | $\text{Workload} = 0$ | Any | `Potentially eliminates manual intervention time and accelerates system recovery once automated {tool_clause} through {action_phrase}.` |
| `Not Yet Triggered Automated` | $0 < \text{Workload} < 60$ | $= 1$ | `Potentially eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event) once automated {tool_clause} through {action_phrase}.` |
| `Not Yet Triggered Automated` | $0 < \text{Workload} < 60$ | $> 1$ | `Potentially eliminates {WL} minutes of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) once automated {tool_clause} through {action_phrase}.` |
| `Not Yet Triggered Automated` | $\text{Workload} \ge 60$ | $= 1$ | `Potentially eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event) once automated {tool_clause} through {action_phrase}.` |
| `Not Yet Triggered Automated` | $\text{Workload} \ge 60$ | $> 1$ | `Potentially eliminates {WL_HR} hours of manual operational workload per month (saving {DUR} minutes per event across {EV} monthly events) once automated {tool_clause} through {action_phrase}.` |
| `Partial Automated` | $0 < \text{Workload} < 60$ | $= 1$ | `Reduces monthly operational workload by {WL} minutes (saving {DUR} minutes per event) {tool_clause} through {action_phrase}.` |
| `Partial Automated` | $0 < \text{Workload} < 60$ | $> 1$ | `Reduces monthly operational workload by {WL} minutes (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.` |
| `Partial Automated` | $\text{Workload} \ge 60$ | $= 1$ | `Reduces monthly operational workload by {WL_HR} hours (saving {DUR} minutes per event) {tool_clause} through {action_phrase}.` |
| `Partial Automated` | $\text{Workload} \ge 60$ | $> 1$ | `Reduces monthly operational workload by {WL_HR} hours (saving {DUR} minutes per event across {EV} monthly events) {tool_clause} through {action_phrase}.` |

---

## 2. Decision Table: Action Phrase Mapping

| Input: Category Action | Standardized Output Action Phrase |
|---|---|
| `Auto Housekeeping` | `scheduled automated log and disk housekeeping` |
| `Auto Monitoring` | `continuous proactive monitoring and real-time anomaly detection` |
| `Auto Restart` | `automated service restarts and rapid downtime mitigation` |
| `Health Check` | `automated system health checks and proactive issue prevention` |
| `Self Service Request` | `streamlined self-service execution and eliminating manual ticket handling` |
| `Smart Healing` | `automated fault detection and self-healing recovery` |

---

## 3. Decision Table: Tool Clause Mapping

| Input: Tools Automation | Standardized Output Tool Clause | Catatan Sintaks |
|---|---|---|
| `AION` | `via AION` | Menggunakan preposisi `via` |
| `Shell Script` / `Shell script` | `via Shell Script` | Menggunakan preposisi `via` |
| `Grafana` | `via Grafana` | Menggunakan preposisi `via` |
| `BMC` | `via BMC` | Menggunakan preposisi `via` |
| `DSC` | `via DSC` | Menggunakan preposisi `via` |
| `CICD` | `via CI/CD automation` | Ekspansi akronim menjadi `CI/CD automation` |
| `AO` | `via AO` | Menggunakan preposisi `via` |
| `Not Automate` | `through standardized automation` | Khusus: preposisi `via` ditiadakan, diganti frase |

---

## 4. Decision Table: Hours Number Formatting

| Calculated Value ($\text{Workload} / 60$) | Formatting Rule | Output String Example |
|---|---|---|
| Bilangan Bulat (misal $300 / 60 = 5.0$) | Integer format | `5 hours` |
| Desimal 1 angka di belakang koma (misal $150 / 60 = 2.5$) | 1 decimal format | `2.5 hours` |
| Desimal pecahan berulang (misal $165 / 60 = 2.75$) | Pembulatan 1 decimal (`{hours:.1f}`) | `2.8 hours` |
| Desimal pecahan (misal $100 / 60 = 1.666...$) | Pembulatan 1 decimal (`{hours:.1f}`) | `1.7 hours` |

---

## 5. Decision Matrix Examples Across Core Combinations

| Sample No | Category Action | Tools Automation | Status Triggered | Dur | Ev | WL | Output Benefit Statement |
|---|---|---|---|---|---|---|---|
| **1** | `Auto Monitoring` | `Shell Script` | `Fully Automated` | 5 | 5 | 25 | `Eliminates 25 minutes of manual operational workload per month (saving 5 minutes per event across 5 monthly events) via Shell Script through continuous proactive monitoring and real-time anomaly detection.` |
| **2** | `Auto Monitoring` | `Grafana` | `Not Yet Triggered Automated` | 15 | 30 | 450 | `Potentially eliminates 7.5 hours of manual operational workload per month (saving 15 minutes per event across 30 monthly events) once automated via Grafana through continuous proactive monitoring and real-time anomaly detection.` |
| **3** | `Smart Healing` | `Shell Script` | `Fully Automated` | 30 | 1 | 30 | `Eliminates 30 minutes of manual operational workload per month (saving 30 minutes per event) via Shell Script through automated fault detection and self-healing recovery.` |
| **4** | `Smart Healing` | `AION` | `Not Yet Triggered Automated` | 20 | 1 | 20 | `Potentially eliminates 20 minutes of manual operational workload per month (saving 20 minutes per event) once automated via AION through automated fault detection and self-healing recovery.` |
| **5** | `Self Service Request` | `AION` | `Partial Automated` | 15 | 11 | 165 | `Reduces monthly operational workload by 2.8 hours (saving 15 minutes per event across 11 monthly events) via AION through streamlined self-service execution and eliminating manual ticket handling.` |
| **6** | `Auto Restart` | `Shell Script` | `Fully Automated` | 10 | 30 | 300 | `Eliminates 5 hours of manual operational workload per month (saving 10 minutes per event across 30 monthly events) via Shell Script through automated service restarts and rapid downtime mitigation.` |
| **7** | `Health Check` | `CICD` | `Not Yet Triggered Automated` | 10 | 1 | 10 | `Potentially eliminates 10 minutes of manual operational workload per month (saving 10 minutes per event) once automated via CI/CD automation through automated system health checks and proactive issue prevention.` |
| **8** | `Smart Healing` | `Not Automate` | `Not Yet Triggered Automated` | 0 | 1 | 0 | `Potentially eliminates manual intervention time and accelerates system recovery once automated through standardized automation through automated fault detection and self-healing recovery.` |
| **9** | `Self Service Request` | `Not Automate` | `Fully Automated` | 5 | 1 | 5 | `Eliminates 5 minutes of manual operational workload per month (saving 5 minutes per event) through standardized automation through streamlined self-service execution and eliminating manual ticket handling.` |

