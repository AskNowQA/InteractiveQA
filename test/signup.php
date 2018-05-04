<?php 
    header("Content-Type: text/html; charset=utf8");

    if(!isset($_POST['submit'])){
        exit("wrong submit");
    }

    $name=$_POST['name'];//post get username
    $password=$_POST['password'];//post get psw

    include('connect.php');//
    $q="insert into user(id,username,password) values (null,'$name','$password')";//insert sql to database
    $reslut=mysql_query($q,$con);//do the sql
    
    if (!$reslut){
        die('Error: ' . mysql_error());//
    }else{
        echo "signup success";//
    }

    

    mysql_close($con);//

?>