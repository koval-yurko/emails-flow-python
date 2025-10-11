PROMPT_EMAIL_PROCESS = """
Have next HTML of email message:
{email_content}

Analyze all available Posts mentioned there across all Sections (Articles & Tutorials, Opinions & Advice, Launches & Tools, Miscellaneous);
Ignore Sponsored posts.
Extract Posts URLs from title's links.
Provide minimal text content for each Post mentioned there.
Make Post classification according to the next hierarchy:

Domain - Level 1 (# Title)
Category - Level 2 (## Subtitle)
Tag - Level 3 (- Item)
	
```
# Work

## Business
- Entrepreneurship
- Freelancing
- Small Business
- Startups
- Venture Capital

## Marketing
- Advertising
- Branding
- Content Marketing
- Content Strategy
- Digital Marketing
- SEO
- Social Media Marketing
- Storytelling For Business

## Leadership
- Employee Engagement
- Leadership Coaching
- Leadership Development
- Management
- Meetings
- Org Charts
- Thought Leadership

## Remote Work
- Company Retreats
- Digital Nomads
- Distributed Teams
- Future Of Work
- Work From Home

# Technology

## Artificial Intelligence
- ChatGPT
- Conversational AI
- Deep Learning
- Large Language Models
- Machine Learning
- NLP
- Voice Assistant
- Computer Vision
- Neural Networks
- Generative AI
- AI Ethics
- Natural Language Generation
- Reinforcement Learning
- AI Models
- OpenAI
- Claude
- Gemini
- Midjourney
- Stable Diffusion
- DALL-E
- AI Agents
- Prompt Engineering
- Fine-tuning
- Transfer Learning
- Transformers

## Blockchain
- Bitcoin
- Cryptocurrency
- Decentralized Finance
- Ethereum
- NFT
- Web3
- Smart Contracts
- Solidity
- Polygon
- Cardano
- Solana
- Binance Smart Chain
- Chainlink
- Uniswap
- MetaMask
- Wallet
- Mining
- Staking
- DAO (Decentralized Autonomous Organization)
- DApps
- Layer 2
- Cross-chain
- Tokenomics

## Data Science
- Analytics
- Data Engineering
- Data Visualization
- Database Design
- SQL
- Big Data
- Data Mining
- Statistical Analysis
- Predictive Analytics
- Business Intelligence
- ETL
- Data Pipeline
- Apache Spark
- Hadoop
- Tableau
- Power BI
- Python for Data Science
- R Programming
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebooks
- Apache Airflow
- Snowflake
- Data Warehouse

## Gadgets
- eBook
- Internet of Things
- iPad
- Smart Home
- Smartphones
- Wearables
- Virtual Reality
- Augmented Reality
- Gaming Consoles
- Drones
- Smart Speakers
- Fitness Trackers
- Smartwatches
- Tablets
- Laptops
- Headphones
- Smart TV
- Electric Vehicles
- Tesla
- Home Automation
- Smart Security
- Alexa
- Google Home
- Apple Watch
- AirPods

## Makers
- 3D Printing
- Arduino
- DIY
- Raspberry Pi
- Robotics
- Electronics
- Microcontrollers
- Sensors
- Actuators
- PCB Design
- Soldering
- CAD Design
- CNC
- Laser Cutting
- IoT Projects
- Home Automation
- ESP32
- STM32
- FPGA
- Embedded Systems
- Circuit Design
- Hardware Hacking
- Open Source Hardware

## Security
- Cybersecurity
- Data Security
- Encryption
- Infosec
- Passwords
- Privacy
- Ethical Hacking
- Penetration Testing
- Network Security
- Application Security
- Cloud Security
- Identity Management
- Multi-factor Authentication
- Zero Trust
- GDPR
- Compliance
- Security Auditing
- Incident Response
- Malware
- Phishing
- Social Engineering
- Vulnerability Assessment
- Security Operations Center
- SIEM
- Firewall

## Tech Companies
- Amazon
- Apple
- Google
- Mastodon
- Medium
- Meta
- Microsoft
- Tiktok
- Twitter
- Netflix
- Tesla
- Uber
- Airbnb
- Spotify
- Adobe
- Salesforce
- Oracle
- IBM
- Intel
- NVIDIA
- AMD
- Samsung
- Huawei
- Zoom
- Slack
- Discord
- LinkedIn
- YouTube
- Instagram
- WhatsApp
- Snapchat
- Pinterest
- Reddit
- Shopify
- PayPal
- Square
- Stripe

## Design
- Accessibility
- Design Systems
- Design Thinking
- Graphic Design
- Icon Design
- Inclusive Design
- Product Design
- Typography
- UX Design
- UX Research
- UI Design
- Visual Design
- Interaction Design
- Motion Design
- Brand Design
- Web Design
- Mobile Design
- Prototyping
- Wireframing
- User Testing
- Design Tools
- Figma
- Sketch
- Adobe Creative Suite
- Canva
- InVision
- Principle
- Framer
- Usability Testing
- Information Architecture
- Service Design

## Product Management
- Agile
- Innovation
- Kanban
- Lean Startup
- MVP
- Product
- Strategy
- Scrum
- Product Marketing
- Product Analytics
- User Stories
- Roadmapping
- Feature Prioritization
- A/B Testing
- Customer Research
- Market Research
- Competitive Analysis
- Product-Market Fit
- Go-to-Market Strategy
- KPIs
- OKRs
- Product Launch
- Stakeholder Management
- Requirements Gathering
- User Journey Mapping
- Product Lifecycle
- Growth Hacking
- Metrics
- Conversion Optimization
- Customer Success

## Cloud Computing
- AWS
- Microsoft Azure
- Google Cloud Platform
- Cloud Architecture
- Serverless
- Containers
- Microservices
- Cloud Migration
- Multi-cloud
- Hybrid Cloud
- Edge Computing
- CDN
- Cloud Security
- SaaS
- PaaS
- IaaS
- Cloud Storage
- Load Balancing
- Auto Scaling
- Cloud Monitoring

## Networking & Infrastructure
- 5G
- WiFi
- Network Protocols
- TCP/IP
- DNS
- VPN
- Network Administration
- Network Monitoring
- Bandwidth
- Latency
- Edge Computing
- Content Delivery Network
- Network Security
- Software Defined Networking
- Network Virtualization

## Emerging Technologies
- Quantum Computing
- Extended Reality (XR)
- Metaverse
- Digital Twins
- Autonomous Vehicles
- Biotechnology
- Nanotechnology
- Space Technology
- Green Technology
- Sustainable Tech
- Clean Energy
- Smart Cities
- Industry 4.0
- Digital Transformation

# Software Development

## Programming
- Android Development
- Coding
- Flutter
- Frontend Engineering
- iOS Development
- Mobile Development
- Software Engineering
- Web Development
- Game Development
- Desktop Application Development
- API Development
- Microservices Architecture
- Full-Stack Development
- Cross-Platform Development
- Progressive Web Apps (PWA)
- Serverless Development

## Programming Languages
- Angular
- CSS
- HTML
- Java
- JavaScript
- Nodejs
- Python
- React
- Ruby
- Typescript
- C++
- C#
- Go (Golang)
- Rust
- PHP
- Swift
- Kotlin
- Vue.js
- Svelte
- Dart
- Scala
- C
- SQL
- R
- SASS/SCSS
- Next.js
- Express.js
- Django
- Flask
- Spring Boot
- Laravel
- Ruby on Rails

## DevOps
- AWS
- Databricks
- Docker
- Kubernetes
- Terraform
- Azure
- Google Cloud Platform (GCP)
- Jenkins
- GitLab CI/CD
- GitHub Actions
- Ansible
- Chef
- Puppet
- Vagrant
- Helm
- Prometheus
- Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Redis
- MongoDB
- PostgreSQL
- MySQL
- Nginx
- Apache
- CircleCI
- ArgoCD
- Istio

## Operating Systems
- Android
- iOS
- Linux
- MacOS
- Windows
- Ubuntu
- CentOS
- Red Hat Enterprise Linux (RHEL)
- Debian
- Fedora
- FreeBSD
- Unix

## Databases & Storage
- MySQL
- PostgreSQL
- MongoDB
- Redis
- Cassandra
- Oracle Database
- Microsoft SQL Server
- SQLite
- Neo4j
- Amazon DynamoDB
- Firebase
- Supabase

## Messaging & Streaming
- RabbitMq
- Kafka
- Redpanda
- NATS JetStream
- AWS SQS/SNS

## Testing & Quality Assurance
- Jest
- Cypress
- Selenium
- JUnit
- Mocha
- PyTest
- Postman
- Insomnia
- SonarQube
- TestRail

## Version Control & Collaboration
- Git
- GitHub
- GitLab
- Bitbucket
- Subversion (SVN)
- Mercurial

## Design & UI/UX
- Figma
- Sketch
- Adobe XD
- InVision
- Zeplin
- Tailwind CSS
- Bootstrap
- Material-UI
- Ant Design

## Development Tools & IDEs
- Visual Studio Code
- IntelliJ IDEA
- Eclipse
- Sublime Text
- Atom
- Vim
- Emacs
- Android Studio
- Xcode

# Society

## Economics
- Basic Income
- Debt
- Economy
- Inflation
- Stock Market

## Education
- Charter Schools
- Education Reform
- Higher Education
- PhD
- Public Schools
- Student Loans
- Study Abroad
- Teaching

## Finance
- 401k
- Investing
- Money
- Philanthropy
- Real Estate
- Retirement

## Law
- Criminal Justice
- Law School
- Legaltech
- Social Justice
- Supreme Court

## Transportation
- Logistics
- Public Transit
- Self Driving Cars
- Trucking
- Urban Planning

## Science
- Archaeology
- Astronomy
- Astrophysics
- Biotechnology
- Chemistry
- Ecology
- Genetics
- Geology
- Medicine
- Neuroscience
- Physics
- Psychology
- Space

## Mathematics
- Algebra
- Calculus
- Geometry
- Probability
- Statistics

```

Select domains, categories and tags only from provided list.
In case there is some new tag - as key companies/products mentioned in the post - add it to newTags list


You must format your output as a JSON value that adheres to a given "JSON Schema" instance.

"JSON Schema" is a declarative language that allows you to annotate and validate JSON documents.

For example, the example "JSON Schema" instance {{"properties": {{"foo": {{"description": "a list of test words", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}}}
would match an object with one required property, "foo". The "type" property specifies "foo" must be an "array", and the "description" property semantically describes it as "a list of test words". The items within "foo" must be strings.
Thus, the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of this example "JSON Schema". The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Your output will be parsed and type-checked according to the provided schema instance, so make sure all fields in your output match the schema exactly and there are no trailing commas!

Here is the JSON Schema instance your output must adhere to. Include the enclosing markdown codeblock:
```json
{json_schema}
```
"""
