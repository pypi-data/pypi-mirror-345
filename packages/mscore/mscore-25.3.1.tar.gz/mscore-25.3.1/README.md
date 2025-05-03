<p align="center">
    <a href="https://www.riskadjustmentmodel.com/" target="_blank">
        <img src="https://ram-site-assets-pub.s3.us-east-1.amazonaws.com/images/mscore_registered_logo_updated_subtitle.png">
    </a>
</p>

---

M<span style="font-size:.8em;">SCORE<sup>®</sup></span> is a python package designed to streamline the CMS-HCC model risk score calculation process for health plans and providers participating in Medicare Advantage and value-based care. It provides a SAS®-free alternative to produce HCCs and risk scores. It streamlines your data processing for enhanced accessibility and allows you to keep your data secure in-house, so you can focus on execution of your risk adjustment strategy.

## Features
- **Implement Anywhere**: M<span style="font-size:.8em;">SCORE<sup>®</sup></span> unlocks multiple integration opportunities including real-time scoring, embedding in EHR or enterprise data warehouse, incorporating into cloud applications, and traditional batch scoring.
- **SAS<sup><span style="font-size:.8em;">&reg;</span></sup>-Free**:  Create HCC and risk scores without SAS<sup><span style="font-size:.8em;">&reg;</span></sup> software, reduce software license costs and the headache of recoding and maintaining the software in another programming language.
- **Enhanced Output**:  M<span style="font-size:.8em;">SCORE<sup>®</sup></span> provides the numeric relative factor value for each HCC assigned to a person allowing for a deeper understanding of how each factor contributes to an individual's overall risk score.
- **Reliable**: Validated on over 1 million plus enrollees. M<span style="font-size:.8em;">SCORE<sup>®</sup></span> is rigorously tested and updated with each HCC model release.
- **CMS-HCC Model Support**: Supports HCC models V22, V24, and V28, covering payment years 2021-2025 with upgrades for each release from CMS (Initial, Mid-Year, Final).
- **Easy to Set Up & Maintain**: Easily installed and upgraded using pip, Python's standard package manager.
- **Platform Compatibility**: Compatible with Windows, Mac, and Linux operating systems.
- **Optimized Performance**: Efficient processing with fast runtimes, ensuring quick and accurate risk score calculations.
- **Improved Data Security**: Securely process personal health information within your organization's IT infrastructure.


## Installation

    pip install mscore

## Registration

Registration is required to use the <code>mscore</code> package.  Please visit https://riskadjustmentmodel.com/registration to create user account and obtain a license key.

## Trial License

After you've installed <code>mscore</code>, run the following command to activate your free 30-day trial. An internet connection is required to activate & run the package.

    mscore -a <license key>

## Subscribe

To use M<span style="font-size:.8em;">SCORE<sup>®</sup></span> for internal business operations beyond the 30-day trial period, a pay-as-you-go subscription and payment method is needed. Please set up your payment method in our [customer portal](https://riskadjustmentmodel.com/account/login/) on the billing tab. To license M<span style="font-size:.8em;">SCORE<sup>®</sup></span> for commercial purposes other than internal business operations, please [contact us](https://riskadjustmentmodel.com/contact-us) directly for alternative licensing.

For more information on pricing, please see our product page.  If you do not see a price you like, then please email us so we can discuss your requirements.

Academic users are eligible for a free license of our software. Please [contact us](https://riskadjustmentmodel.com/contact-us) to obtain your complimentary academic license.


## Basic Use

Before you can run your scores, you will need to generate an authorization token object.

```python
import sourcedefender  #This package is required at the top
from mscore import AuthorizeLicense, MScore

auth = AuthorizeLicense(staging_key).validate()
```
> **<span style="color:orange">_NOTE:_</span>** You must import sourcedefender at the top of every package that imports MScore.

The <code>mscore</code> class requires 7 arguments in order to run with 2 optional arguments.

### Required
* <code>authorizer</code> - The authorization token obtained when <span style="font-family:courier-new">AuthroizeLicense</span> is ran
* <code>year</code> 
* <code>version</code>
* <code>model</code> 
* <code>person_data</code> (Pandas DataFrame, csv, or parquet file)
* <code>diag_data</code> (Pandas DataFrame, csv, or parquet file)
* <code>columns</code> 

### Optional
* <code>dev</code> (boolean) - Runs the application in 'Development' mode

 **_NOTE:_**  The example below assumes you already have a [Pandas](https://pandas.pydata.org/) DataFrame generated for your person and diagnosis datasets.
If you don't have this data yet and want to test <code>mscore</code>, download our synthetic data files here:
* [Person File](https://mph-static-site.s3.amazonaws.com/static/tutorial-files/person.csv)
* [Diagnosis File](https://mph-static-site.s3.amazonaws.com/static/tutorial-files/diag.csv)


```python
import sourcedefender
import pandas as pd
from mscore import AuthorizeLicense, MScore

# Generate DataFrames if using our test files
person_df = pd.read_csv('person.csv')
diag_df = pd.read_csv('diag.csv')

auth = AuthorizeLicense(staging_key).validate()

model = MScore(
    authorizer = auth,
    year = '2025', 
    version = 'V28',
    model = 'CMS-HCC',
    person_data = person_df,
    diag_data = diag_df,
    columns = 'all-fields',
)

scores = model.score_mscore()

print(scores.risk_scores)
print(scores.relative_factors)
```
The resulting 'scores' output is a data model object of pandas.DataFrames. You can access your risk scores or relative factors data sets by calling the respective model name from the grouped data model. 
- <span style="font-family:courier-new">scores.risk_scores</span>
- <span style="font-family:courier-new">scores.relative_factors</span>

From here you can proceed to use the risk score or relative factor DataFrames for further downstream processing or utilize the [Pandas](https://pandas.pydata.org/docs/user_guide/index.html) built-in methods to save to a file type of your choosing.

### Supported Data
The <code>mscore</code> class attributes, <code>person_data</code> and <code>diag_data</code>, will accept a Pandas.DataFrame object, CSV or Parquet filepath directly without the need to load your input data to DataFrame first. The resulting outputs will be a Pandas DataFrame object.

### Supported Environments

M<span style="font-size:.8em;">SCORE<sup>®</sup></span> is designed to be universally compatible, ensuring seamless integration across various platforms.

•	Operating Systems:  Windows, macOS, Linux
•	Python Versions: 3.10 or greater (both 32-bit and 64-bit architectures)

If your required environment is not listed, please contact us as support@riskadjustmentmodel.com for an alternate solution.

## User Resources
For a more in-depth dive into all available model options, arguments, and reference documents, visit our [User Guides](https://riskadjustmentmodel.com/resources/user-guides).

## Support

We are experts in Risk Adjustment and we're here to help. Whether it's general questions, billing, or integration support, please [contact us](https://riskadjustmentmodel.com/contact-us)📧. We are here to make risk scoring easy.

## Stay Connected

Please [subscribe](https://riskadjustmentmodel.com/articles#userEmail) to our newsletter, to receive updates on new M<span style="font-size:.8em;">SCORE<sup>®</sup></span> features, model releases, tutorials, and to stay up-to-date on the latest news in risk adjustment. 

## Legal

To review the M<span style="font-size:.8em;">SCORE<sup>®</sup></span> license agreement, please visit [EULA](https://riskadjustmentmodel.com/legal/eula) webpage.