package com.monitorrail.service;

import net.sf.mpxj.*;
import net.sf.mpxj.reader.UniversalProjectReader;
import org.springframework.stereotype.Service;
import com.monitorrail.util.CryptoUtil;

import javax.crypto.SecretKey;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.file.Files;
import java.util.*;

@Service
public class MppParseService {

    public Map<String,Object> parseMppEncrypted(byte[] encryptedContent, byte[] iv, SecretKey key) throws Exception {
        // Decrypt in memory
        byte[] plain = CryptoUtil.decryptBytes(encryptedContent, key, iv);

        // Save temp file
        File temp = File.createTempFile("proj-", ".mpp");
        try (FileOutputStream fos = new FileOutputStream(temp)) {
            fos.write(plain);
            fos.flush();
        }

        Map<String,Object> result = parseMppFile(temp);

        // Secure delete
        overwriteAndDelete(temp);
        Arrays.fill(plain, (byte)0);

        return result;
    }

    private Map<String,Object> parseMppFile(File file) throws Exception {
        UniversalProjectReader reader = new UniversalProjectReader();
        ProjectFile project = reader.read(file);

        Map<String,Object> out = new LinkedHashMap<>();
        out.put("projectName", project.getProjectProperties() != null ? project.getProjectProperties().getProjectTitle() : null);
        out.put("start", project.getStartDate());
        out.put("finish", project.getFinishDate());

        List<Map<String,Object>> tasksOut = new ArrayList<>();
        for (Task t : project.getTasks()) {
            if (t == null || t.getName() == null) continue;
            Map<String,Object> m = new LinkedHashMap<>();
            m.put("id", t.getID());
            m.put("name", t.getName());
            m.put("wbs", t.getOutlineNumber());
            m.put("start", t.getStart());
            m.put("finish", t.getFinish());
            m.put("baselineStart", t.getBaselineStart());
            m.put("baselineFinish", t.getBaselineFinish());
            m.put("duration", t.getDuration() != null ? t.getDuration().getDuration() : null);
            m.put("percentComplete", t.getPercentageComplete());
            m.put("cost", t.getCost());
            m.put("actualCost", t.getActualCost());
            m.put("baselineCost", t.getBaselineCost());
            // timephased
            List<Map<String,Object>> tpList = new ArrayList<>();
            List<TimephasedValue> tv = t.getTimephasedValues();
            if (tv != null) {
                for (TimephasedValue v : tv) {
                    Map<String,Object> tp = new LinkedHashMap<>();
                    tp.put("start", v.getStart());
                    tp.put("finish", v.getFinish());
                    tp.put("value", v.getValue());
                    tpList.add(tp);
                }
            }
            m.put("timephased", tpList);
            // predecessors
            List<Map<String,Object>> preds = new ArrayList<>();
            if (t.getPredecessors() != null) {
                for (Relation r : t.getPredecessors()) {
                    Map<String,Object> rm = new HashMap<>();
                    Task target = r.getTargetTask();
                    rm.put("id", target != null ? target.getID() : null);
                    rm.put("type", r.getType() != null ? r.getType().toString() : null);
                    rm.put("lag", r.getLag());
                    preds.add(rm);
                }
            }
            m.put("predecessors", preds);

            tasksOut.add(m);
        }
        out.put("tasks", tasksOut);

        List<Map<String,Object>> resources = new ArrayList<>();
        for (Resource r : project.getResources()) {
            if (r == null || r.getName() == null) continue;
            Map<String,Object> rm = new LinkedHashMap<>();
            rm.put("id", r.getID());
            rm.put("name", r.getName());
            rm.put("type", r.getType() != null ? r.getType().toString() : null);
            rm.put("standardRate", r.getStandardRate());
            resources.add(rm);
        }
        out.put("resources", resources);

        return out;
    }

    private void overwriteAndDelete(File f) throws Exception {
        long length = f.length();
        try (FileOutputStream fos = new FileOutputStream(f)) {
            byte[] zeros = new byte[4096];
            long written = 0;
            while (written < length) {
                int toWrite = (int)Math.min(zeros.length, length - written);
                fos.write(zeros, 0, toWrite);
                written += toWrite;
            }
            fos.flush();
        }
        Files.deleteIfExists(f.toPath());
    }
}

