package tech.sda.iqa.util;

import java.util.Set;

import org.json.JSONArray;
import org.json.JSONObject;

public class TempalateGeneratorServer {
/* json format for python server
 * {
 * "entities":[{"ent":"<http://dbpedia.org/resource/Barack_Obama>"}],
 * "predicates":[{"pred":"<http://dbpedia.org/ontology/region>"},
 * 				 {"pred":"<http://dbpedia.org/ontology/largestCity>"}]
 * }
 * 
 * 
 * 
 * {
 * "predicates":[{"pred":"http://dbpedia.org/ontology/capital"}],
 * "entities":[{"ent":"<http://dbpedia.org/resource/Germany>"}]
 * }
 */

	public static String generator(Set<String> predicate, Set<String> resource) throws Exception{
		JSONObject jo_ent = new JSONObject();
		for (String s : resource)
			jo_ent.put("ent", s);
		
		JSONObject jo_pred = new JSONObject();
		for (String p : predicate)
			jo_pred.put("pred", "<"+p+">");
		
		JSONArray ja_ent = new JSONArray();
		ja_ent.put(jo_ent);
		
		JSONArray ja_pred = new JSONArray();
		ja_pred.put(jo_pred);
		
		JSONObject mainObj = new JSONObject();
		mainObj.put("predicates", ja_pred);
		mainObj.put("entities", ja_ent);
		
		//mainObj to python server 
    	request_server http = new request_server();
    	System.out.println(mainObj);
    	String response_post_id = http.sendPost("http://localhost:8080/templates", mainObj.toString());
		return response_post_id;
	}

}
