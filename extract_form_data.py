import boto3
import time
import json

def extract_form_data(document_name = 'i20.pdf', input_path = 'input_pdf/', bucket_name = 'testbucket-lordpara', region_name = 'us-east-2'):
    """Extract form data from a PDF document using Amazon Textract and save the results to a JSON file."""
    
    s3 = boto3.client('s3', region_name=region_name)
    textract = boto3.client('textract', region_name=region_name)
    input_file = input_path + document_name
    output_file = "amazon_textract_raw/" + document_name.replace(".pdf", "_analysis.json")

    print("Uploading "+ document_name +" to S3...")
    s3.upload_file(input_file, bucket_name, document_name)

    print("Starting Textract job...")
    response = textract.start_document_analysis(
        DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': document_name}},
        FeatureTypes=["FORMS"]
    )

    job_id = response['JobId']
    print(f"Started job with ID: {job_id}")

    while True:
        status = textract.get_document_analysis(JobId=job_id)
        status_str = status['JobStatus']
        print(f"Job status: {status_str}")
        if status_str in ['SUCCEEDED', 'FAILED']:
            break
        time.sleep(5)

    pages = [status]
    while 'NextToken' in status:
        status = textract.get_document_analysis(JobId=job_id, NextToken=status['NextToken'])
        pages.append(status)

    all_blocks = [b for p in pages for b in p['Blocks']]
    json_output = json.dumps(all_blocks, indent=4)

    with open(output_file, "w") as f:
        f.write(json_output)

    print(f"✅ Done! Extracted data saved to {output_file}")
    print("-----------------------------------------------------------")
