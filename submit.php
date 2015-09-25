<!-- TODO
Test this more thoroughly. Check for security! 

Also may want to generate a logon key for users after the form is submitted.
This could be a random hash value. They should write down this value for later
use, maybe on our index.html there could be a form to enter the key into which
takes them to a portal page to see results of their experiments. This would be
an easy way to have user accounts simply create a login script (python or php)
that checks a new table in the database (user) for a row with the key in order
to login. -->

<?php

// TODO: remove the following block comment when ready to deploy code
/*
echo "<pre>";
//echo exec("sudo find / -name {$_FILES['filePath']['tmp_name']}");
print_r($_FILES['filePath']);
echo '<br>';
echo is_uploaded_file($_FILES['filePath']['tmp_name']);

// check file upload
$file_info = $_FILES['filePath'];

$uploaddir = '/tmp/';


//$uploaddir = '~/code/NRL/UWNet-web-interface/uploads/';
$uploadfile = $uploaddir . basename($file_info['name']);
echo '<br>';

echo $uploadfile;
echo '<br>';
if (move_uploaded_file($_FILES['filePath']['tmp_name'], $uploadfile)) {
echo "file is valid";
}

else {
echo "upload attack";
}
echo "</pre>";

exit();
*/

// TODO: change
$contact_email = 'uwnetadmin@cs.ucla.edu';

try {
    // all fields expecting a number must have a numeric value
    if (!(
        is_numeric($_POST['mpwr']) &&
        is_numeric($_POST['lpwr']) &&
        is_numeric($_POST['ppwr']) &&
        is_numeric($_POST['mbkn']) &&
        is_numeric($_POST['lbkn']) &&
        is_numeric($_POST['pbkn']) &&
        is_numeric($_POST['mmod']) &&
        is_numeric($_POST['lmod']) &&
        is_numeric($_POST['pmod']) &&
        is_numeric($_POST['rptt'])
       ))
    {
        throw new RuntimeException('Ensure that the parameters are numerical');
    }

    // create new associative array containing numeric vals
    // (<string> plus <int> is <int>, thanks PHP!)
    $nums = array(
    'mpwr' => $_POST['mpwr'] + 0,
    'lpwr' => $_POST['lpwr'] + 0,
    'ppwr' => $_POST['ppwr'] + 0,
    'mbkn' => $_POST['mbkn'] + 0,
    'lbkn' => $_POST['lbkn'] + 0,
    'pbkn' => $_POST['pbkn'] + 0,
    'mmod' => $_POST['mmod'] + 0,
    'lmod' => $_POST['lmod'] + 0,
    'pmod' => $_POST['pmod'] + 0,
    'rptt' => $_POST['rptt'] + 0
    );

    // all numeric values must be positive integers
    if (!(
        is_int($nums['mpwr']) && $nums['mpwr'] > 0 &&
        is_int($nums['lpwr']) && $nums['lpwr'] > 0 &&
        is_int($nums['ppwr']) && $nums['ppwr'] > 0 &&
        is_int($nums['mbkn']) && $nums['mbkn'] > 0 &&
        is_int($nums['lbkn']) && $nums['lbkn'] > 0 &&
        is_int($nums['pbkn']) && $nums['pbkn'] > 0 &&
        is_int($nums['mmod']) && $nums['mmod'] > 0 &&
        is_int($nums['lmod']) && $nums['lmod'] > 0 &&
        is_int($nums['pmod']) && $nums['pmod'] > 0 &&
        is_int($nums['rptt']) && $nums['rptt'] > 0
       ))
    {
        throw new RuntimeException('Ensure that all numerical parameters are positive integers');
    }

    // max must be greater than min
    if (!(
        ($nums['mpwr'] >= $nums['lpwr']) &&
        ($nums['mbkn'] >= $nums['lbkn']) &&
        ($nums['mmod'] >= $nums['lmod'])
       ))
    {
        throw new RuntimeException('Ensure that for all numerical parameters, max &gt;= min');
    }

    // step size must evenly divide interval
    if (
        (($nums['mpwr'] != $nums['lpwr']) && 
        (($nums['mpwr'] - $nums['lpwr']) % $nums['ppwr'] != 0)) ||

        (($nums['mbkn'] != $nums['lbkn']) &&
        (($nums['mbkn'] - $nums['lbkn']) % $nums['pbkn'] != 0)) ||

        (($nums['mmod'] != $nums['lmod']) &&
        (($nums['mmod'] - $nums['lmod']) % $nums['pmod'] != 0))
       )
    {
        throw new RuntimeException('Ensure that (max - min) mod step == 0, or that max == min');
    }

    // connect to DB and execute query
    $username = getenv('USERNAME') ? : getenv('USER');

    // TODO: have mysql prompt for login password, change the following line
    $mysql_handle = mysql_connect('localhost', 'mark', 'pass')
        or die('Unable to connect');
        // TODO: give better die warnings; maybe do internal error warning
    $db_handle = mysql_select_db('UWNet', $mysql_handle)
        or die('Unable to select the database');

    // TODO: sanitize testData
    // TODO: Read on 'SQL injection'
    $sanitized_email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);

    if (!filter_var($sanitized_email, FILTER_VALIDATE_EMAIL))
    {
        throw new RuntimeException('Bad email');
    }



    // check file upload
    $file_info = $_FILES['filePath'];


    if (!isset($file_info['error']) || is_array($file_info['error']))
    {
        throw new RuntimeException('Invalid parameters.');
    }

    // check the error value
    switch ($file_info['error'])
    {
        case UPLOAD_ERR_OK:
            break;
        case UPLOAD_ERR_NO_FILE:
            throw new RuntimeException('No file sent');
        case UPLOAD_ERR_INI_SIZE:
        case UPLOAD_ERR_FORM_SIZE:
            throw new RuntimeException('File size error');
        default:
            throw new RuntimeException("Unknown error with file. Contact sysadmin at $contact_email.");
    }

    // TODO: may want to change number of bytes to allow for max upload size
    // remember to change this in php.ini and index.html also!!
    if ($file_info["size"] > 2000000)
    {
        throw new RuntimeException('File too big! Please use a file smaller than 2 Mb.');
    }

    /*
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    if (false === $ext = array_search($finfo->file($file_info['tmp_name']),
            array(
                'jpg' => 'image/jpeg',
                'png' => 'image/png',
                'gif' => 'image/gif',
            ),
            true)
       )
    {
        throw new RuntimeException('invalid file format');
    }
    */


    $unique_file_name = hash('md5', basename($file_info['name']) . time());
    $uploadfile = '/tmp/' . $unique_file_name;

    if (!move_uploaded_file($file_info['tmp_name'], $uploadfile))
    {
        throw new RuntimeException('file could not be uploaded');
    }
    $date_submitted = date('Y-m-d H:i:s');

    // construct query
    $query = 
    "INSERT INTO InputQueue
    (
    mpwr,	lpwr,	ppwr,
    mbkn,	lbkn,	pbkn,
    mmod,	lmod,	pmod,
    rptt,
    testData,
    email,
    dateSubmitted
    )
    VALUES
    (
    {$nums['mpwr']},	{$nums['lpwr']},	{$nums['ppwr']},
    {$nums['mbkn']},	{$nums['lbkn']},	{$nums['pbkn']},
    {$nums['mmod']},	{$nums['lmod']},	{$nums['pmod']},
    {$nums['rptt']},
    '$uploadfile',
    '$sanitized_email',
    '$date_submitted'
    )";
    $result = mysql_query($query);
    mysql_close($mysql_handle);

    if (!$result) // mysql insert succeeds!
    {
        throw new RuntimeException('mysql insert failed');
    }

    echo '<p>Request submitted successfully! Results will be sent to the following email address:</p>';
    echo "<p>$sanitized_email</p>";
    echo "<p>If this is incorrect, please contact us at $contact_email</p>";
    // TODO: Specify contact email in line above
}
catch (RuntimeException $e)
{
    $error_msg = $e->getMessage();
    echo "<p>$error_msg</p>";
}

?>
