<?php
    $server="localhost:8888";//
    $db_username="";//
    $db_password="";//

    $con = mysql_connect($server,$db_username,$db_password);//link to database
    if(!$con){
        die("can't connect".mysql_error());//
    }
    
    mysql_select_db('test',$con);//select database
?>