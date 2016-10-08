package tech.sda.iqa.util;

//import static spark.Spark.*;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

//import javax.net.ssl.HttpsURLConnection;

import org.json.JSONObject;

public class request_server {
	
	private final String USER_AGENT = "Mozilla/5.0";
	
    public static void main(String[] args) throws Exception {
        System.out.println("score"+sendToVec("leaders","father"));
        
    }
    
    private String sendGet(String microservice_url) throws Exception {

		String url = microservice_url;
		
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		// optional default is GET
		con.setRequestMethod("GET");

		//add request header
		con.setRequestProperty("User-Agent", USER_AGENT);

		int responseCode = con.getResponseCode();
		System.out.println("\nSending 'GET' request to URL : " + url);
		System.out.println("Response Code : " + responseCode);

		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();

		//print result
		return response.toString();

	}
    private String sendPost(String microservice_url,String microservice_url_Parameters) throws Exception {
    	//Not tested. Need to be modified for sending result. 
		String url = microservice_url;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//add reuqest header
		con.setRequestMethod("POST");
		con.setRequestProperty("User-Agent", USER_AGENT);
		con.setRequestProperty("Accept-Language", "en-US,en;q=0.5");

//		String urlParameters = "sn=C02G8416DRJM&cn=&locale=&caller=&num=12345";//this is where data is passed. 	
		String urlParameters = microservice_url_Parameters;
		// Send post request
		con.setDoOutput(true);
		DataOutputStream wr = new DataOutputStream(con.getOutputStream());
		wr.writeBytes(urlParameters);
		wr.flush();
		wr.close();

		int responseCode = con.getResponseCode();
		System.out.println("\nSending 'POST' request to URL : " + url);
		System.out.println("Post parameters : " + urlParameters);
		System.out.println("Response Code : " + responseCode);

		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();
		
		//print result
		return response.toString();

	}
    private static float sendToVec(String word1, String word2) throws Exception
    {
    	String urlParameters = "word1=" + word1 + "&word2=" + word2;
    	String url = "http://localhost:8080/similarity";
    	request_server http = new request_server();
    	String response_post_id = http.sendPost(url, urlParameters);
    	return Float.parseFloat(response_post_id);
    }
    private String sendToYoda(String microservice_url,String question) throws Exception{
    	//The way api works is as follows 
    	// send Post request to url with q = "question" and response will be a question id 
    	// send a get request in the following format q/<id> to retrive answer in the form of json
    	
    	request_server http = new request_server();
    	String urlParameter = "text=" +  question;
    	System.out.println("sending a post request and the response is ");
    	String post_microservice_url = microservice_url + "/q";
    	String response_post_id = http.sendPost(post_microservice_url,urlParameter);
    	System.out.println(response_post_id);
    	//the output is a json object in the form 
    	//{"id":"1805010721"}
    	
    	JSONObject jsonObject = new JSONObject(response_post_id);
    	response_post_id = jsonObject.get("id").toString();
    	System.out.println(response_post_id);
    	
    	System.out.println("sending a get request and the response is ");
    	String microservice_get_url = microservice_url + "/q/" + response_post_id;
    	String response_get_answer = http.sendGet(microservice_get_url);
    	System.out.println(response_get_answer);
    	return response_get_answer;
    	
    }
}