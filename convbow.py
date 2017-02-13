from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from config import Config
import neuralbow
import utils


class ConvolutionalBagOfWordsModel(neuralbow.NeuralBagOfWordsModel):
    '''An attention-based neural bag of words model.'''

    def __init__(self, config, vocab, label_space_size):
        super(ConvolutionalBagOfWordsModel, self).__init__(config, vocab, label_space_size)

    def summarize(self, embed):
        '''Convolve input embeddings to get context-based embeddings'''
        self.dynamic_embs = utils.conv1d(embed, self.config.word_emb_size, self.config.attn_window)
        return tf.reduce_sum(self.dynamic_embs, 1)


class ConvolutionalBagOfWordsRunner(neuralbow.NeuralBagOfWordsRunner):
    '''Runner for the attention bag of words model.'''

    def __init__(self, config, session, model_class=ConvolutionalBagOfWordsModel, verbose=True):
        super(ConvolutionalBagOfWordsRunner, self).__init__(config, session,
                                                            model_class=model_class,
                                                            verbose=verbose)

    def visualize(self, verbose=True):
        with tf.variable_scope('Linear', reuse=True):
            W = tf.get_variable('Matrix').eval()  # logistic regression weights (label embeddings)
        if self.config.query:
            split = self.config.query
        else:
            split = 'test'
        for batch in self.reader.get([split]):
            dynamic_embs = self.session.run(self.model.dynamic_embs,
                                            feed_dict={self.model.notes: batch[0],
                                                       self.model.lengths: batch[1],
                                                       self.model.labels: batch[2]})
            # TODO compute dot product of dynamic embeddings with label embeddings
            print(dynamic_embs.shape)


def main(_):
    config = Config()
    config_proto = tf.ConfigProto()
    config_proto.gpu_options.allow_growth = True
    with tf.Graph().as_default(), tf.Session(config=config_proto) as session:
        ConvolutionalBagOfWordsRunner(config, session).run()


if __name__ == '__main__':
    tf.app.run()