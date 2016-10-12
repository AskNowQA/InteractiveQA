package tech.sda.iqa.util.annotation;


import java.util.HashSet;
import java.util.Set;

//import org.aksw.asknow.util.EntityAnnotate;

public class EntityAnnotation {

	@SuppressWarnings("null")
	public static String getEntityAnnotation(String nlQuery) {
		//System.out.println("::"+nlQuery);
		String dbpRes = "";
		//dbpRes = Fox.annotate(nlQuery);
		//System.out.println(dbpRes.size());
		if (dbpRes == ""){
			
			dbpRes=Spotlight.getDBpLookup(nlQuery);
		}
		if (dbpRes.isEmpty()){
			System.out.print("SPOTLIGHT: Spotlight Could not annotate the Entity **0");
			return null;
		}
		//System.out.print("SPOTLIGHT: "+dbpRes +" **"+dbpRes.size() );
		return dbpRes;
	}
	public static Set<String> getFOXAnnotation(String nlQuery) {
		//System.out.println("::"+nlQuery);
		Set<String> dbpRes = new HashSet<String>();
		dbpRes = Fox.annotate(nlQuery);
		
		if (dbpRes.isEmpty()){
			System.out.println("FOX Could not annotate the Entity");
			return null;
		}
		System.out.println("FOX: "+dbpRes );
		return dbpRes;
	}
	
}
