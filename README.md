<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/helen1806/SOFTWARE-AGING-MONITOR">
    
  </a>

<h3 align="center">ETL Studio</h3>

  <p align="center">
    A full-stack ETL pipeline application for uploading, cleaning, transforming, querying, and storing datasets with an interactive UI and real-time data profiling.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#future enhancementsp">Future Enhancements</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Dashboard Screenshot][product-screenshot]]

Data preprocessing is a critical step in machine learning, data warehousing, and business intelligence workflows. Inconsistent or unclean data can significantly impact downstream processes.
ETL Studio addresses this by providing intuitive tools to clean, transform, and standardize datasets.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

**Languages**

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
* ![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
* ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
* ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

**Frameworks & Libraries**

* ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
* ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
* · Monaco Editor · REST APIs

**Database & Backend**

* ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
* ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
* psycopg2

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This section explains how to run **ETL Studio** locally. Follow the steps below to set up the project on your machine.

### Prerequisites

Ensure the following are installed before proceeding:

* Python 3.9+
* PostgreSQL

  
### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/helen1806/SOFTWARE-AGING-MONITOR.git
   cd ETL_STUDIO
   ```

2 Set up environment variables — create a `.env` file in the root directory:
   ```env
   SUPABASE_URL=your_url
   SUPABASE_KEY=your_key
   DATABASE_URL=your_postgres_connection

   ```

3 Start the Flask server
   ```bash
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

**ETL Studio** provides a complete pipeline from raw CSV upload to cleaned datasets along with a SQL editor.

---

### Step 1 — Upload Dataset

1. Open the dashboard
2. Drag & drop CSV files into the sidebar
3. Supports multiple file uploads

Validation rules:
- CSV files only
- Max size: 50MB
- Encoding handling (UTF-8 / Latin-1)
- Rejects empty files

---

### Step 2 — Data Profiling

Once uploaded, the system automatically generates:
- Column data types
- Null count & percentage
- Unique values


---

### Step 3 — Data Transformation

Available operations:
- Remove nulls
- Drop duplicates
- Lowercase / Uppercase
- Trim whitespace
- Fill nulls (mean, mode, empty)
- Delete column

Features:
- Unlimited operations
- History tracking
- Reset to original dataset

---

### Step 4 — SQL Editor

Run queries directly on your processed data using the built-in SQL editor:


Results are displayed within the preview panel.

---

### Step 5 — Load to Database

Push your cleaned dataset to Supabase:
- Automatically creates table schema
- Maps pandas → PostgreSQL types
- Bulk inserts data efficiently

---

### Step 6 — Export Data

Download your processed dataset in:
- CSV format
- JSON format

---

### Step 7 — Dataset Management

- Sidebar shows all uploaded datasets
- Switch between datasets
- Delete datasets
- Persistent working state

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- Future Enhancements-->
## Future Enhancements

- [ ] **AI-Powered Data Extraction**
  - Extract structured tables from PDFs and unstructured files
  - Automatically convert them into clean datasets suitable for processing

- [ ] **AI Query Assistant**
  - Users can describe tasks :
    - "Split this table into two based on condition"
    - "Find top 10 records by revenue"
  - System generates optimized SQL queries automatically

- [ ] **Smart Transformation Suggestions**
  - AI analyzes dataset patterns and recommends cleaning steps  
  - Example:
    - Detect null-heavy columns → suggest fill/drop  
    - Detect inconsistent formats → suggest normalization  

- [ ] **Context-Aware Query Recommendations**
  - Suggest queries based on existing database tables  
  - Helps users explore and analyze datasets faster  

- [ ] **Scheduled ETL Pipelines**
  - Automate data processing at fixed intervals  
  - Enable continuous data ingestion and transformation  

- [ ] **Cloud Deployment**
  - Deploy using Docker + cloud platforms (AWS / GCP / Azure)  
  

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also open an issue with the tag "enhancement". Don't forget to give the project a star!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/Feature`)
3. Commit your Changes (`git commit -m 'Add some Feature'`)
4. Push to the Branch (`git push origin feature/Feature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Helen Sebastian - helenmarys1023@gmail.com

Project Link: [https://github.com/helen1806/SOFTWARE-AGING-MONITOR](https://github.com/helen1806/SOFTWARE-AGING-MONITOR)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/helen-sebastian
[product-screenshot]: images/dashboard.png
