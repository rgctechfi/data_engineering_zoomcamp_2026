## Module 2 Homework

> In case you don't get one option exactly, select the closest one 

For the homework, we'll be working with the _green_ taxi dataset located here:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download`

To get a `wget`-able link, use this prefix (note that the link itself gives 404):

`https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/`

### Assignment

So far in the course, we processed data for the year 2019 and 2020. Your task is to extend the existing flows to include data for the year 2021.

![alt text](dataset.png)

As a hint, Kestra makes that process really easy:
1. You can leverage the backfill functionality in the [scheduled flow](../../../02-workflow-orchestration/flows/05_gcp_taxi_scheduled.yaml) to backfill the data for the year 2021. Just make sure to select the time period for which data exists i.e. from `2021-01-01` to `2021-07-31`. Also, make sure to do the same for both `yellow` and `green` taxi data (select the right service in the `taxi` input).
2. Alternatively, run the flow manually for each of the seven months of 2021 for both `yellow` and `green` taxi data. Challenge for you: find out how to loop over the combination of Year-Month and `taxi`-type using `ForEach` task which triggers the flow for each combination using a `Subflow` task.

### Quiz Questions

Complete the quiz shown below. It's a set of 6 multiple-choice questions to test your understanding of workflow orchestration, Kestra, and ETL pipelines.

## *1) Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?*

<b>
<div style="color: #5bde7e;">
Add this after extract in the kestra flow:

 - id: size_output
    type: io.kestra.plugin.core.storage.Size
    uri: "{{ outputs.extract.outputFiles[inputs.taxi ~ '_tripdata_' ~ inputs.year ~ '-' ~ inputs.month ~ '.csv'] }}"

<div align="center">
  <img src="size_output.png" width="45%">
</div>

When the prompt appears configure month: 12 and year: 2020

<div align="center">
  <img src="image.png" width="45%">
</div>

1 MiB = 1024 x 1024 byte = 1 048 576 bytes

134481400 byte(octet) = 134,4814 MegaByte (Megaoctet)
BUT 1 MB = 0,953674 MiB (mebioctet)

134481400 byte / 1 048 576 bytes(1MiB)
OR
134,4814 MB * 0,953674 MiB

-> = 128,251457214 MiB

### <u>ANSWER: 128.3 MiB</u>
</div>
</b>


## *2) What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?*

<b>
<div style="color: #5bde7e;">
 ANSWER:

`green_tripdata_2020-04.csv`

variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"

It's like a fstring -> inputs.taxi : green, inputs.year.2020, inputs.months:04

</div>
</b>


## *3) How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?*

<b>
<div style="color: #5bde7e;">

Adding this at the end of the flow:
```yaml
triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    inputs:
      taxi: green

  - id: yellow_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 10 1 * *"
    inputs:
      taxi: yellow
```

And change variable 'file' by:
```yaml
file: "{{inputs.taxi}}_tripdata_{{trigger.date | date('yyyy-MM')}}.csv"
```

You must "force" Kestra to run this flow for the 12 months of 2020.
Go to your personnal workflow or the same as 04_postgres_taxi flow.
Click on the Triggers tab (or directly on the Backfill button at the top right).
Configure the Backfill as follows:
    - Start Date: 2020-01-01
    - End Date: 2020-12-31

<div align="center">
  <img src="backfill_yellow.png" width="45%">
</div>

Configure with the purpose of "each month the process needs to be executed".
2025-01-01 00 00 00 : Ok
For the end of the last month, December, I cannot write the first December 00:00:00 -> because we schedule at 9:00 am !

<div align="center">
  <img src="execution_backfill.png" width="60%">
</div>

<div align="center">
  <img src="schedule_topology.png" width="45%">
</div>


```sql
SELECT count(*) 
FROM public.yellow_tripdata 
WHERE filename LIKE 'yellow_tripdata_2020%';

```


</div>
</b>

- 13,537.299
- 24,648,499
- 18,324,219
- 29,430,127

## *4) How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?*

<b>
<div style="color: #5bde7e;">

<div align="center">
  <img src="backfill_green.png" width="45%">
</div>


```sql
SELECT count(*) 
FROM public.green_tripdata 
WHERE filename LIKE 'green_tripdata_2020%';

```

<div align="center">
  <img src="Q4_green.png" width="45%">
</div>
- 1,734,051


</div>
</b>

## *5) How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?*

<b>
<div style="color: #5bde7e;">

- 1,428,092
- 706,911
- 1,925,152
- 2,561,031

</div>
</b>

## *6) How would you configure the timezone to New York in a Schedule trigger?*

<b>
<div style="color: #5bde7e;">



</div>
</b>
- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration  
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration  

## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw2
* Check the link above to see the due date

## Solution

Will be added after the due date
