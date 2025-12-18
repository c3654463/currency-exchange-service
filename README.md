# Currency Exchange Service

**Student:** Om Patel (c3654463)  
**Module:** COMP637 - Cloud Computing Development  
**Institution:** Leeds Beckett University  
**Level:** 6 (Final Year)  
**Submission:** December 2025

---

A Flask-based REST API for real-time currency conversion, deployed on AWS Elastic Beanstalk. Built this for my cloud computing module to get hands-on experience with PaaS deployment. Chose currency exchange over the typical unit converter because I travel quite a bit and always wondered how these rates actually work behind the scenes.

## What it does

Converts between eight major currencies (GBP, USD, EUR, JPY, AUD, CAD, CHF, CNY) using live exchange rates from an external API. Nothing overcomplicated - just a clean REST API with proper error handling and caching to avoid hammering the external service.

## Quick Start

### Prerequisites

- Python 3.11 or newer
- Free API key from ExchangeRate-API
- AWS account with EB CLI (for deployment)

### Local Setup

1. Clone or download this repo

2. Set up a virtual environment:
```bash
python -m venv venv
```

3. Activate it:
- Windows: `venv\Scripts\activate.bat`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Get your API key:
- Go to https://www.exchangerate-api.com/
- Sign up with your email
- They'll email you a key straightaway

6. Update the API key in `.env`:
```
EXCHANGE_API_KEY=065daf069dc593d23d98abd1
```

7. Start the service:
```bash
python app.py
```

Should see "Running on http://127.0.0.1:5000" if everything's working.

## Using the API

### Health Check
```
http://localhost:5000
```

Returns JSON showing service status and available endpoints.

### Convert Currencies
```
http://localhost:5000/api/v1/convert?from_currency=GBP&to_currency=USD&amount=100
```

Converts 100 GBP to USD. Change the parameters as needed.

### Get Exchange Rates
```
http://localhost:5000/api/v1/rates?base_currency=GBP
```

Returns all supported exchange rates relative to GBP (or whatever base currency you specify).

### Command-Line Client

Built a CLI tool as well:

```bash
# Convert currency
python client.py convert --from GBP --to USD --amount 100

# View rates
python client.py rates --base GBP
```

Note: Update `BASE_URL` in client.py to point to your deployed URL for cloud testing.

## Deploying to AWS Elastic Beanstalk

This was the most interesting part of the project. Here's what I did:

### Setup

1. Installed AWS CLI and EB CLI
2. Configured AWS credentials (`aws configure`)
3. Created IAM user with appropriate permissions
4. Set region to eu-west-2 (London - closest to Leeds)

### Deployment Process

1. Initialize EB in project directory:
```bash
eb init
```

Selected Python 3.11 platform, eu-west-2 region.

2. Created environment:
```bash
eb create currency-exchange-env
```

Elastic Beanstalk handled the entire infrastructure setup - EC2 instance, security groups, load balancer configuration, everything.

3. Deployed the code:
```bash
eb deploy
```

Takes about 5-10 minutes. EB reads the `Procfile` to know how to run the app (using gunicorn on port 8000).

4. Set environment variables:
```bash
eb setenv EXCHANGE_API_KEY=your_api_key
```

This configures the API key securely without putting it in the codebase.

5. Access the live service:
```bash
eb open
```

Opens your application URL in the browser.

### Key AWS Files

- **Procfile**: Tells EB how to start the application with gunicorn
- **.ebignore**: Specifies what not to upload (venv, local files, etc.)
- **requirements.txt**: Python dependencies EB installs automatically
- **.elasticbeanstalk/config.yml**: EB configuration (created by `eb init`)

The deployment was surprisingly straightforward once I sorted out the IAM permissions. Had to create an elasticbeanstalk-admin group because my user hit the 10 managed policy limit.

## Project Structure

```
currency-exchange-service/
├── app.py              # Main Flask application
├── client.py           # Command-line client
├── requirements.txt    # Python dependencies
├── Procfile            # EB deployment configuration
├── .ebignore           # Files to exclude from deployment
├── .env                # Local API key (git ignored)
└── venv/               # Virtual environment (git ignored)
```

## Supported Currencies

GBP, USD, EUR, JPY, AUD, CAD, CHF, CNY

These cover most common conversions. Could add more but wanted to keep it focused for the assignment.

## Why These Tech Choices?

**Python** - Already comfortable with it from previous modules, and it's quick for prototyping. The requests and Flask libraries make REST API development straightforward.

**Flask** - Lightweight and I've built a few apps with it before. Didn't need Django's full feature set for something this simple, and Flask gets you up and running faster.

**AWS Elastic Beanstalk** - Had used AWS in another module (EC2 instances), so wanted to explore their PaaS offering. After initially attempting Azure and hitting regional restrictions on the free tier, AWS proved more reliable. EB's automatic infrastructure management (scaling, load balancing, monitoring) showed me why PaaS is compelling for small projects.

**gunicorn** - Production-ready WSGI server. Flask's built-in server is only for development, so gunicorn handles concurrent requests properly in production.

**ExchangeRate-API** - Free tier is generous (1500 requests/month), documentation is clear, and it just works. No authentication complexity beyond a simple API key.

## What I Learned

This project genuinely taught me more than just sitting through lectures:

- **PaaS deployment in practice** - Understanding the deployment pipeline, configuration management, and how PaaS abstracts away infrastructure was eye-opening. Reading about it versus actually deploying are completely different.

- **AWS ecosystem** - After using EC2 previously, trying Elastic Beanstalk gave me proper perspective on the differences. EB's deployment process felt more streamlined for simple apps, though AWS's breadth of services can be overwhelming initially.

- **Flask application structure** - Learned to organize routes properly, separate validation logic, use decorators for error handling, and implement caching effectively. The difference between well-designed and poorly-designed APIs became clear.

- **RESTful API design** - Understanding proper HTTP methods, status codes, error responses, and endpoint naming conventions. Plus the importance of clear documentation.

- **Environment variable management** - The distinction between development (.env files) and production (EB environment variables) configurations. Critical for keeping API keys secure.

- **Caching strategies** - Implementing hourly cache refresh for exchange rates taught me about balancing API costs against data freshness. The lru_cache decorator made this straightforward.

Also picked up troubleshooting skills around IAM permissions, understanding how to read CloudWatch logs, and why cold starts matter on free tier instances (first request after idle takes 2-3 seconds while the instance spins up).

## Challenges I Faced

Won't pretend this was smooth sailing:

- **PowerShell execution policies** on Windows were annoying initially. Spent time figuring out why the virtual environment wouldn't activate properly. Switched to Command Prompt which was more reliable.

- **Environment variables complexity** - Took a while to understand the difference between .env for local development and EB setenv for cloud deployment. Made the mistake of not setting both initially.

- **Azure regional restrictions** - Initially planned to use Azure but hit "RequestDisallowedByAzure" errors across multiple UK and European regions, even with Azure for Students subscription. Policy restrictions on educational accounts made deployment impossible. This actually became a learning point about cloud provider differences.

- **IAM permission issues on AWS** - Hit the 10 managed policy limit on my IAM user. Had to create an elasticbeanstalk-admin group and assign policies there instead. Learned about AWS's policy architecture the hard way.

- **Getting first deployment working** - EB's configuration seemed complicated initially. Understanding Procfile syntax, the relationship between requirements.txt and EB's build process, and how environment variables flow through took some trial and error.

- **Cold start latency** - Was surprised that the first request after being idle takes 2-3 seconds on free tier. Makes sense now (instance needs to spin up) but caught me off guard during testing.

The most challenging aspects were understanding AWS/EB configuration and navigating cloud provider limitations. Writing the Flask code was actually straightforward once I had the structure sorted. The deployment itself was surprisingly easy once configuration was correct - literally just `eb deploy`.

## What Surprised Me

- **How much PaaS handles automatically** - Auto-scaling, load balancing, HTTPS certificates, monitoring. Don't have to think about any of it. Massive difference from manually setting up VMs.

- **How easy deployment actually was** - Once the configuration was sorted, literally just `eb deploy` and it works. Expected it to be way more complicated based on the initial setup complexity.

- **Provider variation in free tier access** - Different cloud providers have vastly different restrictions on educational/free accounts. Azure's regional policies were much stricter than AWS's.

The external API integration was easier than expected too. Good documentation helps massively. ExchangeRate-API's straightforward JSON responses meant minimal parsing logic.

## If I Had More Time

Would probably add:

- **User authentication** - Even basic JWT tokens would make this more production-ready
- **Historical rate data and charts** - Store rates over time, show trends, add visualization
- **More currencies** - Currently just eight, could expand to 20-30 easily
- **Rate limiting** - Prevent API abuse with proper throttling
- **Database for caching** - Use Redis or similar instead of in-memory caching for persistence across restarts
- **Comprehensive monitoring** - Set up CloudWatch alarms for errors, response times, API usage
- **CI/CD pipeline** - Automate deployment with GitHub Actions or similar

But for coursework demonstrating cloud deployment and PaaS understanding, this covers what's needed. The focus was deployment architecture rather than feature completeness.

## Known Issues

Being honest about limitations:

- Relies entirely on one external API - if ExchangeRate-API goes down, this is useless. Should implement fallback to alternative providers.
- First request after idle period is slow (cold start on free tier). Acceptable for demo, would need reserved instances for production.
- No authentication - fine for coursework demo, terrible for real deployment.
- Error messages could be more helpful in some cases. Generic 500 errors don't tell users much.
- No rate limiting - could be abused if public. Would need API gateway or application-level throttling.
- In-memory caching means cache is lost on restart. Should use persistent cache like Redis.

These would all need addressing for a real service, but are acceptable trade-offs for an academic project demonstrating cloud concepts.

## Tech Stack Summary

- **Backend:** Flask (Python 3.11)
- **Deployment:** AWS Elastic Beanstalk (PaaS)
- **Web Server:** gunicorn (production WSGI server)
- **External API:** ExchangeRate-API (free tier)
- **Environment:** Python virtual environment
- **Region:** eu-west-2 (London)
- **Instance:** t2.micro (free tier eligible)

## Cost Analysis

Total cost: £0

AWS free tier covers this easily:
- 750 hours/month of t2.micro EC2 instances (enough for 24/7 operation)
- 5GB of S3 storage
- 1GB of data transfer out

ExchangeRate-API's free tier (1500 requests/month) is more than sufficient for testing and demonstration. No credit card charges incurred.

## Assignment Context

This was developed for the COMP637 Cloud Computing Development module at Leeds Beckett University (Level 6). The assignment required:

- Selection and justification of cloud provider
- Development of a web service with RESTful API
- Deployment using PaaS or IaaS
- Creation of a client application
- Comprehensive report (3000-4000 words)
- Screenshots demonstrating deployment and functionality
- Critical evaluation of implementation and cloud technologies

The accompanying report contains detailed analysis of:
- Cloud computing fundamentals and service models
- AWS vs Azure vs GCP comparison and selection rationale
- Architectural decisions and design patterns
- Complete deployment process with evidence
- Critical evaluation including challenges, solutions, and learning outcomes
- Comparative analysis of cloud providers based on hands-on experience

## Troubleshooting

**Service won't start locally?**
- Check your API key is correct in `.env`
- Verify virtual environment is activated (should see `(venv)` in prompt)
- Try reinstalling dependencies: `pip install -r requirements.txt`

**Getting 503 errors?**
- External API might be down or rate limited
- Verify your API key is valid at exchangerate-api.com
- Check your internet connection

**AWS deployment fails?**
- Ensure EB CLI is authenticated: `aws sts get-caller-identity`
- Check IAM permissions include Elastic Beanstalk access
- Verify Procfile exists and has no file extension
- Check EB logs: `eb logs`

**500 errors on AWS?**
- API key likely not set. Run: `eb setenv EXCHANGE_API_KEY=your_key`
- Check logs for Python errors: `eb logs`
- Verify requirements.txt includes all dependencies

**Virtual environment won't activate (Windows)?**
- Use Command Prompt instead of PowerShell
- Or run: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process` in PowerShell first

## Contact

Om Patel  
O.Patel2393@student.leedsbeckett.ac.uk  
Leeds Beckett University

---

Built over a few weekends as part of my final year cloud computing module. Learned more from actually building and deploying this than from sitting through lectures if I'm honest. The combination of practical implementation and theoretical understanding from the coursework has given me genuine confidence in cloud technologies.

The journey from local development through to cloud deployment - including encountering real-world issues like IAM permissions and provider limitations - provided valuable experience that purely theoretical study couldn't match. Particularly interesting was comparing different cloud providers firsthand and understanding why certain architectural decisions matter in practice.

If you're a marker reading this - the full report with comparative analysis, architectural diagrams, screenshots, and detailed evaluation is in the accompanying Word document. This service was genuinely deployed to AWS and tested extensively, not just written about theoretically.
