import { motion } from 'framer-motion';

const ThoughtProcess = ({ content }) => {
  if (!content) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="thought-process"
    >
      <span className="thought-label">AI Rationale</span>
      <p className="whitespace-pre-wrap">{content}</p>
    </motion.div>
  );
};

export default ThoughtProcess;
