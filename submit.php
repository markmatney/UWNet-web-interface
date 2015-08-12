<?php

// all fields expecting a number must have a numeric value
if (
    is_numeric($_POST['mpwr']) &&
    is_numeric($_POST['lpwr']) &&
    is_numeric($_POST['ppwr']) &&
    is_numeric($_POST['mbkn']) &&
    is_numeric($_POST['lbkn']) &&
    is_numeric($_POST['pbkn']) &&
    is_numeric($_POST['mmod']) &&
    is_numeric($_POST['lmod']) &&
    is_numeric($_POST['pmod'])
   )
{

  // create new associative array containing numeric vals
  $nums = array(
    'mpwr' => $_POST['mpwr'] + 0,
    'lpwr' => $_POST['lpwr'] + 0,
    'ppwr' => $_POST['ppwr'] + 0,
    'mbkn' => $_POST['mbkn'] + 0,
    'lbkn' => $_POST['lbkn'] + 0,
    'pbkn' => $_POST['pbkn'] + 0,
    'mmod' => $_POST['mmod'] + 0,
    'lmod' => $_POST['lmod'] + 0,
    'pmod' => $_POST['pmod'] + 0
  );

  // all numeric values must be integers
  if (
      is_int($nums['mpwr']) &&
      is_int($nums['lpwr']) &&
      is_int($nums['ppwr']) &&
      is_int($nums['mbkn']) &&
      is_int($nums['lbkn']) &&
      is_int($nums['pbkn']) &&
      is_int($nums['mmod']) &&
      is_int($nums['lmod']) &&
      is_int($nums['pmod'])
     )
  {

    // max must be greater than min
    if (
        ($nums['mpwr'] > $nums['lpwr']) &&
        ($nums['mbkn'] > $nums['lbkn']) &&
        ($nums['mmod'] > $nums['lmod'])
       )
    {

      // step size must evenly divide interval
      if (
          (($nums['mpwr'] - $nums['lpwr']) % $nums['ppwr'] == 0) &&
          (($nums['mbkn'] - $nums['lbkn']) % $nums['pbkn'] == 0) &&
          (($nums['mmod'] - $nums['lmod']) % $nums['pmod'] == 0)
         )
      {

        // TODO: sanitize testData and email
        $sanitized_testData = $_POST['testData'];
        $sanitized_email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
        if (!filter_var($sanitized_email, FILTER_VALIDATE_EMAIL))
        {
          echo '<p>problem with email!</p>';
          // TODO: kill
        }

        // construct query
        $query = 
         "INSERT INTO InputQueue
          (
		mpwr,	lpwr,	ppwr,
		mbkn,	lbkn,	pbkn,
		mmod,	lmod,	pmod,
		testData,
		email
          )
          VALUES
          (
		{$nums['mpwr']},	{$nums['lpwr']},	{$nums['ppwr']},
		{$nums['mbkn']},	{$nums['lbkn']},	{$nums['pbkn']},
		{$nums['mmod']},	{$nums['lmod']},	{$nums['pmod']},
		'$sanitized_testData',
		'$sanitized_email'
          )";

        // connect to DB and execute query
        $mysql_handle = mysql_connect('localhost', 'mark', 'pass')
          or die('Unable to connect');
        $db_handle = mysql_select_db('UWNet', $mysql_handle)
          or die('Unable to select the database');
        $result = mysql_query($query);
        mysql_close($mysql_handle);

        // TODO: do error checking

        if ($result)
        {
          echo '<p>Data was inserted correctly!<p>';
          echo '<p>Results will be sent to the following email address:</p>';
          echo "<p>$sanitized_email</p>";
          echo '<p>If this is incorrect, please contact us at [admin uwnet]@cs.ucla.edu</p>';
        }
        else
        {
          echo '<p>ERROR!</p>';
        }
      }
      else
      {
        echo '<p>Ensure that (max - min) mod step == 0</p>';
      }
    }
    else
    {
      echo '<p>Ensure that for all numerical parameters, max &gt; min</p>';
    }
  }
  else
  {
    echo '<p>Ensure that all numerical parameters are integers</p>';
  }
}
else
{
  echo '<p>Ensure that the parameters are numerical</p>';
}

?>
