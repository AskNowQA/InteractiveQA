package tech.sda.iqa.util.annotation;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import org.json.JSONObject;
import org.json.*;

import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.sparql.OneHopRelationQuery;
import tech.sda.iqa.util.request_server;

public class SpotPredicateParser {
	//produces , <http://dbpedia.org/resource/Orangina>      -->ideal
	//<http://dbpedia.org/resource/Prodigy_(online_service)>, members  , .   ---> inverse case
	//people   born  , <http://dbpedia.org/resource/Vienna>,   died  , <http://dbpedia.org/resource/Berlin>, .  ---->chain case
	static ArrayList<String> wordlist= new ArrayList<String>(); //word + highestWord2vecSore
	static ArrayList<Float> pcScore = new ArrayList<Float>(); 
	static ArrayList<String> pcUri = new ArrayList<String>();

	static ArrayList<Float> MAX1pcScore = new ArrayList<Float>(); 
	static ArrayList<String> MAX1pcUri = new ArrayList<String>();
	static ArrayList<Float> MAX2pcScore = new ArrayList<Float>(); 
	static ArrayList<String> MAX2pcUri = new ArrayList<String>();
	static ArrayList<Float> MAX3pcScore = new ArrayList<Float>(); 
	static ArrayList<String> MAX3pcUri = new ArrayList<String>();




	public static Set<String> parser(ArrayList<String> predicateCandidate, Set<String> resourceSpotlight, Nqs q1) {
		wordlist.clear();
		pcScore.clear();
		pcUri.clear();
		ArrayList<String[]>listOfPair = null; //uri label pair;
		Set<String> uriPredicate  = new HashSet<String>();
		//ArrayList<String>temp  = new ArrayList<String>();

		for(String pc :predicateCandidate){
			String[] words = pc.split("\\s+");
			for(int i=0;i<words.length;i++){
				if(words[i].equals("")||words[i].equals(".")||words[i].equals(" ")){

				}
				else{
					wordlist.add(words[i]);
					pcScore.add((float) -1);
					pcUri.add("");

					MAX1pcUri.add("");
					MAX1pcScore.add((float) -1);
					MAX2pcUri.add("");
					MAX2pcScore.add((float) -1);
					MAX3pcUri.add("");
					MAX3pcScore.add((float) -1);}
				System.out.println("asssing=ed");
			}
		}


		for(String dbr : resourceSpotlight){
			listOfPair= OneHopRelationQuery.getPredicateList(dbr); 
			for(int i=0;i<wordlist.size();i++){
				try {
					if(!isOntology(wordlist.get(i)));
					highestmatch(wordlist.get(i),listOfPair,i);
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}

			//			for (int i = 0; i < listOfPair.size(); i++){
			//				String p[] = listOfPair.get(i);
			//				System.out.println(p[0]+"::"+p[1]);//p[0]=uri p[1]=label
			//				
			//			}
		}

		//System.out.println(wordlist);
		for(String uri :pcUri){
			if(uri.contains("dbpedia.org")){
				uriPredicate.add("<"+uri+">");
			}
		}
		//System.out.println(pcUri);
		//System.out.println(uriPredicate);

		q1.jsonPredicate= JSONPred.create(wordlist,MAX1pcUri,MAX1pcScore,MAX2pcUri,MAX2pcScore,MAX3pcUri,MAX3pcScore);
		return uriPredicate;
	}

	private static boolean isOntology(String w) {
		// TODO Auto-generated method stub


		return false;
	}



	private static void highestmatch(String w, ArrayList<String[]> listOfPair, int j) throws Exception {
		// TODO Auto-generated method stub
		System.out.println(MAX1pcScore.get(j)+":"+MAX2pcScore.get(j)+":"+MAX3pcScore.get(j));
		float temp = 0, highest =-1; String higestmatchedRel="";

		for (int i = 0; i < listOfPair.size(); i++){
			String p[] = listOfPair.get(i);
			//System.out.println(p[0]+"::"+p[1]);//p[0]=uri p[1]=label

			String label =p[1];
			String[]firstToken = label.split("\\s+");
			//System.out.println("label"+label);

			temp=request_server.sendToVec(firstToken[0],w);
			//			if(temp>MAX1pcScore[j]){
			////				highest=temp;
			////				higestmatchedRel = p[0];
			//				}

			if(temp>MAX1pcScore.get(j)){
				MAX3pcScore.set(j, MAX2pcScore.get(j));
				MAX2pcScore.set(j, MAX1pcScore.get(j));
				MAX1pcScore.set(j, temp);
				MAX3pcUri.set(j, MAX2pcUri.get(j));
				MAX2pcUri.set(j, MAX1pcUri.get(j));
				MAX1pcUri.set(j, p[0]);
				
			}

			else if(temp>MAX2pcScore.get(j)){
				MAX3pcScore.set(j, MAX2pcScore.get(j));
				MAX2pcScore.set(j, temp);
				MAX3pcUri.set(j, MAX2pcUri.get(j));
				MAX2pcUri.set(j, p[0]);
			}
			else if(temp>MAX3pcScore.get(j)){
				MAX3pcUri.set(j, p[0]);
			}
		}

		pcScore.set(j, MAX1pcScore.get(j));
		pcUri.set(j,MAX1pcUri.get(j));

		//System.out.println(w+" -> "+MAX1pcScore.get(j)+":"+MAX2pcScore.get(j)+":"+MAX3pcScore.get(j));
	}
}