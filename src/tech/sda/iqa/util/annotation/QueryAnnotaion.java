package tech.sda.iqa.util.annotation;

import java.util.HashSet;
import java.util.Set;

import org.json.simple.JSONArray;
//import org.json.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.jsoup.nodes.Element;

import tech.sda.iqa.interactiveqa.Nqs;

public class QueryAnnotaion {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
		testrelanno();
	}
	public static void annotate(Nqs n){
		
		//HashSet<String> rel = new HashSet<String>();
		//rel.add(n.getDesire());
		//rel.add(n.getRelation2());
		n.resourceSpotlightInfo = EntityAnnotation.getEntityAnnotation(n.nlQuery);
		System.out.println(n.resourceSpotlightInfo);
		Set<String> uri = new HashSet() ; 
		JSONParser parser = new JSONParser();
		try{
			Object obj = parser.parse(n.resourceSpotlightInfo);
			JSONArray array = (JSONArray)obj;
//			for (Object link : array) {
//				System.out.println(link.get("uri")); 
//			}
			for (int i = 0; i < array.size(); i++)
			{
				JSONObject obj2 = (JSONObject)array.get(i);
				uri.add((String) obj2.get("uri"));
			}
			n.resourceSpotlight = uri;
		}
		catch (Exception e){
			System.out.println("Some exception at QueryAnnotation");
			e.printStackTrace();
		}
		if (n.resourceSpotlight!=null)
			{n.predicateCandidate = PredicateSpotter.getRelation(n);
			n.predicateCandidate = PredicateAnnotator.annotate(n.predicateCandidate,n.resourceSpotlight);
			}
		else
			{n.predicateCandidate=null;	//TODO
		
			}			
		//System.out.println("Res: "+n.Resource);
		//for (String r : n.Resource){
	//		n.Predicate =RelationAnnotation.getRelAnnotation(rel, r);
		//}
		
	}
	
	static void testrelanno(){
		//Test: RelationAnnotaion
		//<Ques>In which country does the Ganges start?</Ques>
		//<NQS>[WH] = which, [R1] = does, [D] =  country, [R2] = start In, [I] = the  Ganges</NQS>
				HashSet<String> rel = new HashSet<String>();
				rel.add("country");
				rel.add("start");
				String entity = "<http://dbpedia.org/resource/Ganges>";
				//System.out.println(RelationAnnotation.getRelAnnotation(rel, entity));
	}
}
