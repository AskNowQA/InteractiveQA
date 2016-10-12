package tech.sda.iqa.util;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class request_server {
	
	private final String USER_AGENT = "Mozilla/5.0";
	
    public static void main(String[] args) throws Exception {
        System.out.println("score = "+sendToVec("mother","father"));
    }
    
    String sendPost(String microservice_url,String microservice_url_Parameters) throws Exception {
    	//Not tested. Need to be modified for sending result. 
		String url = microservice_url;
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		//add reuqest header
		con.setRequestMethod("POST");
		con.setRequestProperty("User-Agent", USER_AGENT);
		con.setRequestProperty("Accept-Language", "en-US,en;q=0.5");
		con.setRequestProperty("content-type","application/json");

//		String urlParameters = "sn=C02G8416DRJM&cn=&locale=&caller=&num=12345";//this is where data is passed. 	
		String urlParameters = microservice_url_Parameters;
		// Send post request
		con.setDoOutput(true);
		DataOutputStream wr = new DataOutputStream(con.getOutputStream());
		wr.writeBytes(urlParameters);
		wr.flush();
		wr.close();

		int responseCode = con.getResponseCode();
		//System.out.println("\nSending 'POST' request to URL : " + url);
		//System.out.println("Post parameters : " + urlParameters);
		//System.out.println("Response Code : " + responseCode);

		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();
		return response.toString();
	}
    public static float sendToVec(String word1, String word2) throws Exception
    {
    	String urlParameters = "word1=" + word1 + "&word2=" + word2;
    	String url = "http://192.168.2.1:8080/similarity";
    	request_server http = new request_server();
    	String response_post_id = http.sendPost(url, urlParameters);
    	return Float.parseFloat(response_post_id);
    }
    
}