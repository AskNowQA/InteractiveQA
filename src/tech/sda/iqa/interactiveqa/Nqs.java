package tech.sda.iqa.interactiveqa;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;


import org.json.JSONArray;

import lombok.RequiredArgsConstructor;
import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

@RequiredArgsConstructor
@ToString
@Slf4j public class Nqs {

	public final String nlQuery;
	public final String nqs;
	public final String queryID;
	public final String givenSparql;
	
	public Set<String> resourceSpotlight;
	public String resourceSpotlightInfo; //json with scores label uri 
	public Set<String> resourceFOX;
	public Set<String> resDBSpotted;
	
	public JSONArray jsonEntity = new JSONArray();
	public JSONArray jsonPredicate  = new JSONArray();
	
	public Set<String> uriEntity;
	
	public ArrayList<String> predicateCandidate; //
	public String predicateW2VecInfo; //json word,top 2 (score , uri)
	public Set<String> uriPredicate;

	
	//-----------------------------------------------------------------------//
	public String getConcepts(){
		String temp = nqs;

		temp = temp.substring(nqs.indexOf("[Concepts] = [")+14);//, qct.indexOf("]"));

		temp= temp.substring(0, temp.indexOf("]"));
		log.debug(temp);

		return temp;

	}
	public String getRoles(){
		String temp = nqs;
		temp = temp.substring(nqs.indexOf("[Roles] = [")+11);//, qct.indexOf("]"));
		temp= temp.substring(0, temp.indexOf("]"));
		log.debug(temp);
		return temp;

	}
	//-----------------------------------------------------------------------//
	public String setPredicateCandidate(){
		if(!nqs.contains("[Concepts]")){
			
		}
			
		
		return null;
		
	}
	public String getDesire(){
		String temp;
		temp = nqs.substring(nqs.indexOf("[D] =")+5);
		temp = temp.substring(0, temp.indexOf(","));
		return temp.trim();
	}
	public String getRelation2(){
		String temp;
		temp = nqs.substring(nqs.indexOf("[R2] =")+6);
		temp = temp.substring(0, temp.indexOf(","));
		return temp.trim();
	}
	public String getRelation1(){
		String temp;
		temp = nqs.substring(nqs.indexOf("[R1] =")+6);
		temp = temp.substring(0, temp.indexOf(","));
		return temp.trim();
	}
	public String getInput(){
		String temp;
		temp = nqs.substring(nqs.indexOf("[I] =")+5);
		temp = temp.substring(0, (temp+",").indexOf(","));
		return temp.trim();
	}
	public String getWh(){
		String temp;
		temp = nqs.substring(nqs.indexOf("[WH] =")+6);
		temp = temp.substring(0, (temp+",").indexOf(","));
		return temp.trim();
	}
	
	public String getAll(){
		return nlQuery + "\n" + nqs;
	}

	public String getAllInputs(){
		String tempinput="";
		if(nqs.contains("[I]"))
			return getInput();
		else
		{
			tempinput = nqs.substring(nqs.indexOf("[I1_1]"),nqs.indexOf ("["));
			tempinput =tempinput +", "+ nqs.substring(nqs.indexOf("[I1_2]"),nqs.indexOf ("["));
			tempinput =tempinput +", "+ nqs.substring(nqs.indexOf("[I1_3]"),nqs.indexOf ("["));
			return tempinput;
		}
	}
	public String getDesireBrackets()
	{
		//[D] = count(languages)
		String s1;
		s1 = getDesire();
		int i , j;
		i = s1.lastIndexOf("(")+1;
		j = s1.indexOf(')', i);
		return s1.substring(i, j);
	}
	
	//----------------NQS Object "Modi"-fication------------------------------------------------//
	
	public String EntityUpdate(String old_entity ,String new_entity){
		//return : "success" if update is successful
		//return : "denied" if update is unsuccessful
		Set<String> local =new HashSet<String>() ;
		try {
			for (String s : resourceSpotlight){
				if (s.contains(old_entity)){
				s=	new_entity;
				}
				local.add(s);
			}
			resourceSpotlight =local;//TODO check at dbpediaSpotlight 
		}
		catch(Exception e){
			return "denied";
		}
		return "success";
		//
	}
	
	public String EntityAdd(String new_entity){
		//return : "success" if update is successful
		//return : "denied" if update is unsuccessful
		try {
			resourceSpotlight.add(new_entity);
		}
		catch(Exception e){
			return "denied";
		}
		return "success";
	}
	
	public String EntityDelete(String entity ){
		//return : "success" if update is successful
		//return : "denied" if update is unsuccessful
		Set<String> local =new HashSet<String>() ;
		try {
			for (String s : resourceSpotlight){
				if (!s.contains(entity)){ //negation of contains
					local.add(s); 		 //add when match not found
				}
				
			}
			resourceSpotlight =local;
		}
		catch(Exception e){
			return "denied";
		}
		return "success";
		//
	}

}