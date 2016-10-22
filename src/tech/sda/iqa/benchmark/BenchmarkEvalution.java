package tech.sda.iqa.benchmark;

import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.apache.jena.atlas.json.JsonAccess;
import org.json.JSONArray;
import org.json.JSONObject;

import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.interactiveqa.Parser;
import tech.sda.iqa.nqs.QueryBuilder;
import tech.sda.iqa.util.TempalateGeneratorServer;
import tech.sda.iqa.util.annotation.JSONEntity;
import tech.sda.iqa.util.annotation.QueryAnnotaion;
import tech.sda.iqa.util.annotation.SpotPredicateParser;

public class BenchmarkEvalution {
	//private static QueryBuilder qb = new QueryBuilder();
	public static void main(String[] args){ 
		testQALD();
		//testSingle();
	
	}
//	private static void testSingle() {
//		String question ="What is the capital of Germany ?";
//			qb.setQuery(question);
//			qb.buildQuery();
//			String nqs = qb.getCharacterizedString();
//			Nqs q1 = new Nqs(question,nqs,"","");
//			//Interaction : Check query type
//        	QueryAnnotaion.annotate(q1);
//        	System.out.println(q1.predicateCandidate);
//        	//Interaction : Check Predicate and Entity
////        	try {
////				System.out.print(TempalateGeneratorServer.generator(q1.predicateCandidate,q1.resourceSpotlight));
////			} catch (Exception e) {
////				// TODO Auto-generated catch block
////				e.printStackTrace();
////			}
//        	
//		}
		
	
	private static void testQALD() {
		JSONArray final_array = new JSONArray();
		
		for(int i=0;i<349;i++)
		{	System.out.print((i+1)+"\t");
		
			if(i==101||i==113){
				
			}
			else
			final_array.put(evaluate(i));
		}
		
		JSONObject final_obj = new JSONObject();
		final_obj.put("Training", final_array);
		
		try (FileWriter file = new FileWriter("resource/jsonData.txt")) {
//			file.write(final_obj.toJSONString());
			String json_string = final_obj.toString();
			file.write(json_string);
			System.out.println("Successfully Copied JSON Object to File...");
			//System.out.println("\nJSON Object: " + obj);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			System.out.println("UNSuccessfully Copied JSON Object to File...");
			e.printStackTrace();
		}
		
	}
	static JSONObject evaluate(int n){
		List<Nqs> templates = Parser.parse();
		Nqs q1 = templates.get(n);
		System.out.print(q1.nlQuery +"\t");
		QueryAnnotaion.annotate(q1);
		
		
		q1.uriPredicate = SpotPredicateParser.parser(q1.predicateCandidate,q1.resourceSpotlight,q1);
		q1.jsonEntity = JSONEntity.create(q1.resourceSpotlightInfo);
		
		System.out.println();
		try {
			System.out.println("dbo="+q1.uriPredicate);
			System.out.println(	"dbr="+q1.resourceSpotlight);
			//System.out.println(TempalateGeneratorServer.generator(q1.uriPredicate,q1.resourceSpotlight));
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return writeJSON(q1.nlQuery, q1.nqs,q1.jsonEntity,q1.jsonPredicate,n);
	}


	private static  JSONObject writeJSON(String nlQuery, String nqs, JSONArray jsonEntity, JSONArray jsonPredicate, int n) {
		// TODO Auto-generated method stub
		JSONObject final_json = new JSONObject();
		final_json.put("id",n);
		final_json.put("predicate", jsonPredicate);
		final_json.put("entity",jsonEntity);
		final_json.put("nqs",nqs);
		final_json.put("query", nlQuery);
		return final_json;
		
	}
}
