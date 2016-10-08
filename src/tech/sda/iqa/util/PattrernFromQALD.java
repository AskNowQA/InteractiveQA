package tech.sda.iqa.util;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class PattrernFromQALD {
	
	static ArrayList<String> nertags = new ArrayList<String>();
	public static void main(String[] args) {
		readQALDfile();
		}
	
	static void readQALDfile() {
		JSONParser parser = new JSONParser();
		int counter =0;
		String pattern= "";
		 HashMap<String, Integer> hmap = new HashMap<String, Integer>();
		 Set<String> hs = new HashSet<>();
		try {
			Object obj = parser.parse(new FileReader("resource/qald6training.json"));
			JSONObject jsonObject = (JSONObject) obj;
			JSONArray quald = (JSONArray) jsonObject.get("questions");
			Iterator<JSONObject> questions = quald.iterator();
			String sparql;
			while (questions.hasNext()) {
				counter++;
				JSONObject quesObj = questions.next();
				Object ids = quesObj.get("id");
				//if(counter <= 300)
				//{continue;
			//	}
				
				JSONObject query = (JSONObject) quesObj.get("query");
				sparql = (String) query.get("sparql");
				
				
				try{
					pattern = getPattern(sparql);
				}
				catch (NullPointerException ex)
				{
					sparql="#OPEN USER need to add SPARQL #CLOSE";
				}
				//System.out.println(pattern +";;"+ res.size());
				//System.out.println("res count" + res.size());
				
				//if(hmap.get(pattern)==null){
					hs.add(pattern + ";;"+res.size());
				//}
				//else{
				//	int i = hmap.get(pattern);
					
				//} 
					
				res.clear();
				var.clear();
				pred.clear();
			}	
		} 
		
		
		catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		} 
		System.out.println(hs.size());
		for (String s : hs) {
		    System.out.println(s);
		}
		//System.out.println(hmap.toString());

	}


	
	
	
	private static String getPattern(String sparql) {
		// TODO Auto-generated method stub
		//HashMap<String, String> variable,resource,predicate;
		//String s = "This is a sample sentence.";
		String[] tokens = sparql.split("\\s+");
		for (int i = 0; i < tokens.length; i++) {
		   
		    //words[i] = words[i].replaceAll("[^\\w]", "");
			if (tokens[i].contains("/ontology/"))
				tokens[i] = setPredicate(tokens[i]);
			else if(tokens[i].contains("/property/"))
				tokens[i] = setPredicate(tokens[i]);
			else if (tokens[i].contains("http://www.w3.org/1999/02/22-rdf-syntax-ns"))
				tokens[i] = "namespace";
			
			else if(tokens[i].contains("/resource/"))
				tokens[i] = setResource(tokens[i]);
			else if(tokens[i].contains("/yago/"))
				tokens[i] = setResource(tokens[i]);
			
			else if(tokens[i].contains("?"))
				tokens[i] = setVariable(tokens[i]);
			
			else if(tokens[i].contains("#label"))
				tokens[i] = "label";
			
			else if(tokens[i].contains("\'"))
				tokens[i] = "literal";
					
		}
		
		return Arrays.toString(tokens).replaceAll(",","");
	}
	
	
	//--------------------------------------------------------//

	static  ArrayList<String> var = new ArrayList<String>(); 
	static  ArrayList<String> res = new ArrayList<String>();
	static  ArrayList<String> pred = new ArrayList<String>();
	private static String setResource(String key) {
		if (res.contains(key))
			return "res"+ res.indexOf(key);
		else
		{	res.add(key);
			return "res"+ res.indexOf(key);
		}
	}

	private static String setPredicate(String key) {
		if (pred.contains(key))
			return "pred"+ pred.indexOf(key);
		else
		{	pred.add(key);
			return "pred"+ pred.indexOf(key);
		}
	}

	private static String setVariable(String key) {
		if (var.contains(key))
			return "var"+ var.indexOf(key);
		else
		{	var.add(key);
			return "var"+ var.indexOf(key);
		}
	}
	
}
