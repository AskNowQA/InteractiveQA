<?PHP
    header("Content-Type: text/html; charset=utf8");
    if(!isset($_POST["submit"])){
        exit("submit");
    }//exam the submit process

    include('connect.php');//link to connect
    $name = $_POST['name'];//post get username
    $passowrd = $_POST['password'];//post get psw

    if ($name && $passowrd){//if psw and username are not empty
             $sql = "select * from user where username = '$name' and password='$passowrd'";//exam if sql exist
             $result = mysql_query($sql);//exacut sql
             $rows=mysql_num_rows($result);//return 
             if($rows){//0 false 1 true
                   header("refresh:0;url=welcome.html");//if success, to welcome.html
                   exit;
             }else{
                echo "wrong psw or username";
                echo "
                    <script>
                            setTimeout(function(){window.location.href='login.html';},1000);
                    </script>

                ";/;
             }
             

    }else{//if empty
                echo "empty input";
                echo "
                      <script>
                            setTimeout(function(){window.location.href='login.html';},1000);
                      </script>";

                        ;
    }

    mysql_close();//shut down
?>