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
 * {
 * "predicates":[{"pred":"http://dbpedia.org/ontology/capital"}],
 * "entities":[{"ent":"<http://dbpedia.org/resource/Germany>"}]
 * }
 */

	public static String generator(Set<String> predicate, Set<String> resource) throws Exception{
		JSONArray jo_ent = new JSONArray();
		for (String s : resource){
			JSONObject jo_obj = new JSONObject();
			jo_obj.put("ent", s);
			jo_ent.put(jo_obj);
		}
		JSONArray jo_pred = new JSONArray();
		for (String p : predicate){
			JSONObject jo_obj = new JSONObject();
			jo_obj.put("pred", p);
			jo_pred.put(jo_obj);
		}
			//jo_pred.put("pred", predicate);
		
//		JSONArray ja_ent = new JSONArray();
//		ja_ent.put(jo_ent);
//		
//		JSONArray ja_pred = new JSONArray();
//		ja_pred.put(jo_pred);
		
		JSONObject mainObj = new JSONObject();
		mainObj.put("predicates", jo_pred);
		mainObj.put("entities", jo_ent);
		
		//mainObj to python server 
    	request_server http = new request_server();
    	System.out.println(mainObj);
    	String response_post_id = http.sendPost("http://localhost:8080/templates", mainObj.toString());
		return response_post_id;
	}

}
