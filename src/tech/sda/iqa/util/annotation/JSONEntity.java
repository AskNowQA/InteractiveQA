package tech.sda.iqa.util.annotation;

import org.json.JSONArray;
import org.json.*;
//import org.json.simple.parser.ParseException;

public class JSONEntity {
 public static org.json.JSONArray create(String resourceSpotlightInfo){
	 
	 JSONTokener parser = new JSONTokener(resourceSpotlightInfo);
	 JSONArray entity_json = new JSONArray();
	 entity_json.put(parser);
		System.out.println(entity_json);
		return entity_json;
	 
	 
	 
	 
	 
//	 
//	 JSONObject entity_json = new JSONObject();
//	 try {
//		Object obj = parser.parse(resourceSpotlightInfo);
//			entity_json.put("entity", obj);
//			System.out.println(entity_json);
//			return (org.json.JSONArray) obj;
//
//	} catch (ParseException e) {
//		// TODO Auto-generated catch block
//		e.printStackTrace();
//	}
//	return null ;
//	
		
		
 }
}
